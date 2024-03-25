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


app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
