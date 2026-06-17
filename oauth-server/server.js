require('dotenv').config();
const express = require('express');
const validateClient = require('./src/middleware/validateClient');
const {
  passwordGrant,
  clientCredentialsGrant,
  refreshTokenGrant,
  introspect,
  revoke,
} = require('./src/controllers/authController');


const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get('/health', (req, res) => {
    res.status(200).json({ 
        status: 'success', 
        code: 200, 
        data: null, 
        message: 'OAuth Server is healthy', 
        timestamp: new Date().toISOString(), 
        service: 'oauth-server' 
    });
});

app.post('/oauth/token', validateClient, (req, res) => {
    const { grant_type } = req.body;

    switch (grant_type) {
        case 'password':
            return passwordGrant(req, res);
        case 'client_credentials':
            return clientCredentialsGrant(req, res);
        case 'refresh_token':
            return refreshTokenGrant(req, res);
        default:
            return res.status(400).json({ 
                status: "error", 
                code: 400, 
                message: "unsupported_grant_type: Use password, client_credentials, or refresh_token",
                timestamp: new Date().toISOString(),
                service: "oauth-server"
            });
    }
});

app.post('/oauth/introspect', introspect); 
app.post('/oauth/revoke', revoke);

const PORT = process.env.PORT || 3002;
app.listen(PORT, () => {
  console.log(`OAuth Server running on port ${PORT}`);
});