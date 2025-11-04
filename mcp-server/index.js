const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { MongoClient } = require('mongodb');

const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());

const mongoUrl = 'mongodb://34.172.211.78:27017';
const dbName = 'app_auth';
let db;

MongoClient.connect(mongoUrl, { useUnifiedTopology: true }, (err, client) => {
  if (err) {
    console.error('Failed to connect to MongoDB', err);
    return;
  }
  console.log('Connected to MongoDB');
  db = client.db(dbName);
});

app.get('/mcp/sse', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const sendEvent = (data) => {
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  };

  // Example: Send a welcome message
  sendEvent({ message: 'MCP Server Connected' });

  // Keep the connection open
  const intervalId = setInterval(() => {
    sendEvent({ heartbeat: new Date().toISOString() });
  }, 10000);

  req.on('close', () => {
    clearInterval(intervalId);
    res.end();
  });
});

app.post('/mcp/query', async (req, res) => {
    const { query } = req.body;

    if (query === 'get_user_data') {
        const users = await db.collection('users').find({}).toArray();
        res.json(users);
    } else {
        res.status(400).json({ error: 'Unknown query' });
    }
});


app.listen(port, () => {
  console.log(`MCP Server listening at http://localhost:${port}`);
});
