# bSPACE

![converted_image(1)](https://github.com/mrdavtan/bSPACE/assets/21132073/6a9321c2-ba31-4414-9341-51ee8c2f5cd6)

bSPACE is a web-based interactive 3D visualization platform that allows users to explore and interact with a graph of interconnected nodes. The platform incorporates a chat interface powered by OpenAI's GPT-3.5-turbo language model, enabling users to engage in conversational interactions within the application.
Features

Interactive 3D graph visualization using Three.js and 3d-force-graph library
Node customization with sprite text and sphere geometry
Link visualization with text sprites showing the relationship between nodes
Camera orbit animation for enhanced visual experience
Bloom effect using UnrealBloomPass for visual enhancement
Chat interface integrated with OpenAI's GPT-3.5-turbo language model
Responsive design with a floating widget for chat and search functionality

Prerequisites
Before running the bSPACE application, ensure that you have the following:

A modern web browser that supports WebGL and Three.js
An OpenAI API key for the chat functionality

Installation

Clone the bSPACE repository:

```bash

git clone https://github.com/mrdavtan/bSPACE.git

```

Navigate to the project directory:

```bash
cd bSPACE

```
3. Open the index.html file in a text editor.

4. Replace 'YOUR_API_KEY' with your actual OpenAI API key:

```bash

const API_KEY = 'YOUR_API_KEY';

```

5. Save the changes.

## Usage

![Screenshot from 2024-03-30 07-35-03](https://github.com/mrdavtan/bSPACE/assets/21132073/d3adee5a-cb0a-45f8-a136-a34351a602c7)

Open the index.html file in a web browser.
The 3D graph visualization will be displayed, showing interconnected nodes.
Interact with the graph using the following controls:

Click and drag to rotate the graph
Scroll to zoom in and out
Hover over nodes to see their labels


Use the chat interface in the floating widget on the right side of the screen:

Type your message in the input field
Press Enter or click the "Send" button to send the message
The chat history will be displayed above the input field


Explore the graph and engage in conversations using the chat interface.

Customization

To customize the graph data, replace the graph.json file with your own JSON data file.
To modify the appearance and behavior of the graph, you can adjust the parameters and settings in the JavaScript code within the
```
<script> tag.
```
To style the chat interface and floating widget, modify the CSS styles in the ``` <style>``` section of the HTML file.

Dependencies
 utilizes the following libraries and dependencies:

Three.js - JavaScript library for creating 3D graphics in the browser
3d-force-graph - Library for creating interactive 3D force-directed graphs
three-spritetext - Library for rendering text sprites in Three.js
UnrealBloomPass - Three.js post-processing pass for bloom effect

License
This project is licensed under the MIT License.
Acknowledgements

OpenAI for providing the GPT-3.5-turbo language model used in the chat functionality.
The open-source community for developing and maintaining the libraries and tools used in this project.






