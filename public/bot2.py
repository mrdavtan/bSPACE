import os
import io
import sounddevice as sd
import tempfile
import requests
from requests_toolbelt import MultipartEncoder
from pydub import AudioSegment
import wave
import numpy as np
import json
import re
from pyvis.network import Network
from datetime import datetime
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def transcribe_audio(audio_file):
    api_key = os.getenv("OPENAI_API_KEY")
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    data = MultipartEncoder(
        fields={
            "file": ("audio.mp4", open(audio_file, "rb"), "audio/mp4"),
            "model": "whisper-1"
        }
    )
    headers["Content-Type"] = data.content_type
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        result = response.json()
        transcription = result["text"]
        return transcription
    else:
        raise Exception(f"OpenAI API error {response.status_code}: {response.text}")

def query_openai(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4-0125-preview",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        raise Exception(f"OpenAI API error {response.status_code}: {response.text}")

def parse_response(response):
    print(f"Response from OpenAI API: {response}")
    updates = []
    pattern = r'\[\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\s*\]'
    matches = re.findall(pattern, response)
    for match in matches:
        updates.append([match[0], match[1], match[2]])
    print(f"Parsed updates: {updates}")
    nodes = {}
    edges = []
    deletions = []
    for update in updates:
        if len(update) == 3 and update[0] != "DELETE":  # Relationship handling
            node1, relationship, node2 = update
            edges.append({"from": node1, "to": node2, "title": relationship, "label": relationship})
            nodes[node1] = {"id": node1, "label": node1, "color": "#AAAAAA", "article_uuid": "", "article_date": "", "article_source": "", "url": ""}  # Default color and additional properties
            nodes[node2] = {"id": node2, "label": node2, "color": "#AAAAAA", "article_uuid": "", "article_date": "", "article_source": "", "url": ""}
        elif len(update) == 2:  # Color update handling
            node, color = update
            if node in nodes:
                nodes[node]["color"] = color
            else:
                nodes[node] = {"id": node, "label": node, "color": color, "article_uuid": "", "article_date": "", "article_source": "", "url": ""}
        elif update[0] == "DELETE":  # Deletion handling
            deletions.append(update[1])
    print(f"Parsed nodes: {list(nodes.values())}")
    print(f"Parsed edges: {edges}")
    print(f"Parsed deletions: {deletions}")
    return list(nodes.values()), edges, deletions

def create_combined_network(nodes, edges, output_html='combined_network.html'):
    try:
        net = Network(directed=True, width="3000px", height="2000px", bgcolor="#333333")
        added_node_ids = set()  # Track added nodes
        options = {
            "nodes": {
                "font": {
                    "color": "black"
                },
                "color": {
                    "border": "#2B7CE9",
                    "background": "#AAAAAA",
                    "highlight": {
                        "border": "#2B7CE9",
                        "background": "#AAAAAA"
                    }
                }
            },
            "edges": {
                "color": {
                    "color": "#FAE833",
                    "highlight": "#FAE833"
                },
                "smooth": {
                    "type": "dynamic",
                    "forceDirection": "none",
                    "roundness": 0.5
                }
            },
            "physics": {
                "repulsion": {
                    "centralGravity": 0.2,
                    "springLength": 200,
                    "springConstant": 0.05,
                    "nodeDistance": 200,
                    "damping": 0.09
                }
            }
        }
        net.set_options(json.dumps(options))

        for node_data in nodes:
            node_id = node_data['id']
            node_data['uuid'] = str(uuid.uuid4())  # Generate a UUID for each node
            node_data['shape'] = 'circle'  # Set the shape to 'circle'
            node_data['date'] = datetime.now().strftime("%Y-%m-%d")  # Set the current date
            node_data['source'] = 'User Input'  # Set the source as 'User Input'
            node_data['url'] = ''  # Set an empty URL initially
            net.add_node(node_id, **node_data)
            added_node_ids.add(node_id)

        # Add edges to the network, ensuring both nodes exist
        for edge in edges:
            from_id = edge.pop('from')
            to_id = edge.pop('to')
            if from_id in added_node_ids and to_id in added_node_ids:
                edge['arrows'] = 'to'  # Set the arrow direction to 'to'
                net.add_edge(from_id, to_id, **edge)
            else:
                print(f"Skipping edge from {from_id} to {to_id}: One or both nodes not found.")

        # Save and print the network visualization's file name
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_html = f"graphs/combined_network_{current_datetime}.html"
        net.save_graph(output_html)
        print(f"Network visualization saved to {output_html}.")

        # Save the graph as a JSON file with a unique filename
        output_json = f"graphs/chatgpt_graph_{current_datetime}.json"
        data = {
            "nodes": [{"id": node["id"], "label": node["label"], "color": node["color"], "shape": node["shape"],
                       "uuid": node["uuid"], "date": node["date"], "source": node["source"], "url": node["url"]}
                      for node in net.nodes],
            "links": [{"source": edge["from"], "target": edge["to"], "label": edge["label"], "title": edge["title"],
                       "arrows": "to"} for edge in net.edges]
        }
        with open(output_json, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Graph saved as JSON to {output_json}.")
    except Exception as e:
        print(f"Error in create_combined_network: {str(e)}")
        raise

def process_audio(audio_file):
    transcription = transcribe_audio(audio_file)
    print("Transcription:")
    print(transcription)

    base_prompt = """
    Given a transcript, your task is to extrapolate as many relationships and relevant details as possible, organizing them into a list of updates that will be directly parsed by a Python function to create a graph. It's crucial that the updates adhere strictly to the structured formats outlined below, without any additional comments or explanations, to ensure accurate parsing and graph representation.

    Update Formats:

        Relationships between entities: Use the format [ENTITY 1, RELATIONSHIP, ENTITY 2] to indicate a directed relationship, where ENTITY 1 and ENTITY 2 are specific named entities, and RELATIONSHIP describes their connection (e.g., "roommate", "owns", "located in").

        Color updates for entities: If representing an entity with a color, specify this using [ENTITY, COLOR], where COLOR is in hex format.

        Deleting an entity: To indicate the removal of an entity, use ["DELETE", ENTITY].

    Entity Types and Categories:

        Person: Names of individuals (e.g., "Alice", "Dr. John Smith").
        Location: Geographical locations (e.g., "Paris", "Mount Everest").
        Organization: Companies, institutions, governmental entities (e.g., "United Nations", "Google").
        Date/Time: Dates, times, durations (e.g., "January 1, 2020", "next week").
        Numerical: Numbers, monetary figures, percentages (e.g., "100 dollars", "35%").
        Event: Specific events, historical and current (e.g., "World War II", "Olympic Games").
        Product: Products, technology, vehicles (e.g., "iPhone", "Toyota Camry").
        Work of Art: Books, songs, movies (e.g., "The Great Gatsby", "Bohemian Rhapsody").

    Classification Categories:

        General Named Entities: People, Locations, Organizations, and Miscellaneous.
        Temporal Entities: Date/Time and Durations.
        Quantitative Entities: Numerical values, Quantities, Monetary values, Percentages.
        Domain-Specific Entities: Tailored to fields like Medical, Legal, Technical.

    Examples:

    Transcript: "Alice is Bob's roommate. Make her node green."
    Updates: [["Alice", "roommate", "Bob"], ["Alice", "#00FF00"]]

    Transcript: "The conference in Paris was attended by Dr. Emily and Prof. John from MIT. Remove 'conference'."
    Updates: [["Dr. Emily", "attended", "conference"], ["Prof. John", "attended", "conference"], ["conference", "located in", "Paris"], ["DELETE", "conference"]]

Instructions for Processing:

    Ensure the updates are presented exactly as per the formats specified, ready for direct parsing and graph creation. The response must strictly follow the format with no additional comments or explanations, to facilitate accurate and efficient parsing by the Python function.

Please process the following transcript and structure the updates accordingly:
Transcript: {}
Updates:



    """

    formatted_prompt = base_prompt.format(transcription)
    response = query_openai(formatted_prompt)
    nodes, edges, deletions = parse_response(response)
    create_combined_network(nodes, edges)

    print(f"Sending response: {response}")
    return response

# Set up audio recording parameters
sample_rate = 44100  # Sample rate of the recording
channels = 1  # Number of audio channels (mono)

# Create a temporary WAV file to store the recorded audio
with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav_file:
    # Get the temporary WAV file path
    wav_file_path = temp_wav_file.name

    # Create a buffer to store the recorded audio data
    audio_data = []

    # Define the callback function to save the recorded audio to the buffer
    def callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    # Start the audio recording
    print("Recording started. Speak now...")
    with sd.InputStream(samplerate=sample_rate, channels=channels, callback=callback):
        print("Press 'Enter' to stop recording...")
        input()  # Wait for Enter key press to stop recording

    print("Recording finished.")

    # Convert the audio data to a NumPy array
    audio_array = np.concatenate(audio_data, axis=0)
    audio_array = (audio_array * 32767).astype(np.int16)

    # Write the audio data to the temporary WAV file
    with wave.open(wav_file_path, 'wb') as wav_file:
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(2)  # 2 bytes per sample
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_array.tobytes())

# Convert the WAV file to MP4 format
audio = AudioSegment.from_wav(wav_file_path)
mp4_file_path = "recorded_audio.mp4"  # Specify the desired file path for the MP4 file
audio.export(mp4_file_path, format="mp4")

# Process the recorded audio
response = process_audio(mp4_file_path)
print(f"Sent response: {response}")

# Delete the temporary WAV file
os.unlink(wav_file_path)

print(f"Recorded audio saved as: {mp4_file_path}")
