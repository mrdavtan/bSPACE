import os
import io
import sounddevice as sd
import tempfile
import requests
from requests_toolbelt import MultipartEncoder
from pydub import AudioSegment
import wave
import numpy as np

# Create an API client
api_key = os.getenv("OPENAI_API_KEY")

# Set up audio recording parameters
sample_rate = 44100  # Sample rate of the recording
channels = 1  # Number of audio channels (mono)
silence_duration = 4  # Duration of silence to detect (in seconds)
silence_threshold = 0.01  # Amplitude threshold for silence detection

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

# Set up the request data
data = MultipartEncoder(
    fields={
        "file": ("audio.mp4", open(mp4_file_path, "rb"), "audio/mp4"),
        "model": "whisper-1",
    }
)

# Set up the request headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": data.content_type,
}

# Send the POST request to the API
print("Transcribing audio...")
url = "https://api.openai.com/v1/audio/transcriptions"
response = requests.post(url, headers=headers, data=data)

# Print the HTTP response
print("HTTP Response:")
print(f"Status Code: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Content: {response.content}")

# Check the response status code
if response.status_code == 200:
    # Parse the response JSON
    result = response.json()
    transcription = result["text"]
    print("Transcription:")
    print(transcription)
else:
    print(f"Error: {response.status_code} - {response.text}")

# Delete the temporary WAV file
os.unlink(wav_file_path)

print(f"Recorded audio saved as: {mp4_file_path}")
