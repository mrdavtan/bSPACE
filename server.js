import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import cors from 'cors';
import bodyParser from 'body-parser';

const app = express();
const port = 3002;

app.use(cors());

// Necessary for __dirname in ES6 modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

app.use(express.static(path.join(__dirname, 'public')));

app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({limit: '50mb', extended: true, parameterLimit: 50000}));


app.get('/api/graphs', async (req, res) => {
  const graphDirectory = path.join(__dirname, 'public', 'graphs');

  try {
    const files = await fs.promises.readdir(graphDirectory);
    const graphFiles = files.filter(file => file.endsWith('.json'));
    res.json(graphFiles.sort().reverse());
  } catch (err) {
    console.error('Error:', err);
    res.status(500).send('Internal Server Error');
  }
});

app.put('/scene.json', async (req, res) => {
  const sceneFilePath = path.join(__dirname, 'public', 'scene.json');

  try {
    await fs.promises.writeFile(sceneFilePath, JSON.stringify(req.body, null, 2));
    res.sendStatus(200);
  } catch (err) {
    console.error('Error updating scene data:', err);
    res.status(500).send('Internal Server Error');
  }
});

app.post('/save-graph', async (req, res) => {
  const graphData = req.body;

  // Generate a unique filename for the new graph
  const timestamp = new Date().toISOString().replace(/[-:.]/g, '');
  const filename = `graph_${timestamp}.json`;

  try {
    // Save the graph data to a new file in the public/graphs directory
    await fs.promises.writeFile(`public/graphs/${filename}`, JSON.stringify(graphData, null, 2));
    console.log('Graph saved successfully');
    res.sendStatus(200);
  } catch (err) {
    console.error('Error saving graph:', err);
    res.sendStatus(500);
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});


