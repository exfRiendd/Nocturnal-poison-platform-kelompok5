const dotenv = require('dotenv');
dotenv.config();

const express = require('express');
const oauthRoutes = require('./src/routes/oauth.routes');
const errorHandler = require('./src/middleware/errorHandler');


const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'success', code: 200, data: null,
    message: 'OAuth Server is healthy',
    timestamp: new Date().toISOString(), service: 'oauth-server',
  });
});

app.use('/oauth', oauthRoutes);
app.use(errorHandler);

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => console.log(`OAuth Server running on port ${PORT}`));