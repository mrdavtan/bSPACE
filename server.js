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

app.post('/api/start-bot2', (req, res) => {
  const bot2Process = spawn('python', ['bot2.py']);
  bot2Process.on('close', (code) => {
    console.log(`bot2.py process exited with code ${code}`);
  });
  res.sendStatus(200);
});

app.get('/api/latest-graph', (req, res) => {
  fs.readdir('public/graphs', (err, files) => {
    if (err) {
      console.error('Error reading graphs directory:', err);
      res.sendStatus(500);
    } else {
      if (files.length === 0) {
        res.sendStatus(404); // Send 404 if no graph files found
      } else {
        const latestFile = files.sort().pop();
        res.json({ latestFile });
      }
    }
  });
});


app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
