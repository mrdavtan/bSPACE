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



app.get('/api/latest-json', async (req, res) => {
  const directoryPath = path.join(__dirname, 'path_to_your_json_files');

  try {
    const files = await fs.promises.readdir(directoryPath);
    const chatgptFiles = files
      .filter(file => file.startsWith('chatgpt_') && file.endsWith('.json'))
      .map(filename => ({
        filename,
        mtime: fs.statSync(path.join(directoryPath, filename)).mtime
      }))
      .sort((a, b) => b.mtime - a.mtime);

    if (chatgptFiles.length === 0) {
      return res.status(404).send("No matching files found.");
    }

    // Send the most recent file
    res.sendFile(path.join(directoryPath, chatgptFiles[0].filename));
  } catch (err) {
    res.status(500).send("Unable to scan directory: " + err);
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
