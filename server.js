import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import cors from 'cors';

const app = express();
const port = 3002;

app.use(cors());

// Necessary for __dirname in ES6 modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

app.use(express.static(path.join(__dirname, 'public')));


app.get('/api/latest-json', async (req, res) => {
  // ... (keep the existing route handler code)
});

app.get('/api/graphs', async (req, res) => {
  const graphDirectory = path.join(__dirname, 'public', 'graphs');
  try {
    const files = await fs.promises.readdir(graphDirectory);
    const graphFiles = files.filter(file => file.endsWith('.json'));
    res.json(graphFiles);
  } catch (err) {
    console.error('Error:', err);
    res.status(500).send('Internal Server Error');
  }
});


app.get('/api/latest-graph', async (req, res) => {
  const graphDirectory = path.join(__dirname, 'public', 'graphs');
  try {
    const files = await fs.promises.readdir(graphDirectory);
    const jsonFiles = files.filter(file => file.endsWith('.json'));

    if (jsonFiles.length === 0) {
      return res.status(404).send('No graph files found.');
    }

    const latestFile = jsonFiles.reduce((latest, current) => {
      const latestMtime = fs.statSync(path.join(graphDirectory, latest)).mtime;
      const currentMtime = fs.statSync(path.join(graphDirectory, current)).mtime;
      return currentMtime > latestMtime ? current : latest;
    });

    res.json({ latestFile });
  } catch (err) {
    console.error('Error:', err);
    res.status(500).send('Internal Server Error');
  }
});


app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
