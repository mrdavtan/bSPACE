from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import re
import requests
from openai import OpenAI
from dotenv import load_dotenv
from pyvis.network import Network
from datetime import datetime
import uuid

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

def query_openai(prompt):
    """
    Query the OpenAI API using a chat model and return the response.
    Adjust this function based on the latest OpenAI client library support for chat models.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4-0125-preview",  # Specify the chat model you're using
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
    """
    Parse the response to identify relationships, color updates, and deletions.
    """
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
    net = Network(directed=True, width="3000px", height="2000px", bgcolor="#333333")
    added_node_ids = set()  # Track added nodes
    options = """
    {
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
            "smooth": false
        }
    }
    """
    net.set_options(options)

    for node_data in nodes:
        node_id = node_data['id']
        node_data['article_uuid'] = str(uuid.uuid4())  # Generate a UUID for each node
        node_data['shape'] = 'circle'  # Set the shape to 'circle'
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
    output_html = f"combined_network_{current_datetime}.html"
    net.save_graph(output_html)
    print(f"Network visualization saved to {output_html}.")

@app.route('/process', methods=['POST'])
def process_message():
    data = request.get_json()
    user_prompt = data['message']
    print(f"Received user prompt: {user_prompt}")

    base_prompt = """
    Given a prompt, extrapolate as many relationships as possible from it and provide a list of updates.
    If an update is a relationship, provide [ENTITY 1, RELATIONSHIP, ENTITY 2]. The relationship is directed, so the order matters.
    If an update is related to a color, provide [ENTITY, COLOR]. Color is in hex format.
    If an update is related to deleting an entity, provide ["DELETE", ENTITY].

    Example:
    prompt: Alice is Bob's roommate. Make her node green.
    updates:
    [["Alice", "roommate", "Bob"], ["Alice", "#00FF00"]]

    prompt: {}
    updates:
    """

    # Process the user's prompt using your existing code
    formatted_prompt = base_prompt.format(user_prompt)
    response = query_openai(formatted_prompt)
    nodes, edges, deletions = parse_response(response)
    create_combined_network(nodes, edges)

    print(f"Sending response: {response}")
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
