const axios = require('axios');
require('dotenv').config();

const verifyToken = async (req, res, next) => {
  const publicPaths = ['/health', '/metrics', '/oauth/token'];
  
  if (publicPaths.includes(req.path) || (req.path === '/api/citizens' && req.method === 'POST')) {
    return next();
  }

  const authHeader = req.headers['authorization'];

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      status: 'error',
      code: 401,
      message: 'No token provided',
      timestamp: new Date().toISOString(),
      service: 'api-gateway',
    });
  }

  const token = authHeader.split(' ')[1];

  try {
    const oauthServerUrl = process.env.OAUTH_SERVER_URL || 'http://localhost:3002'; 
    
    const response = await axios.post(`${oauthServerUrl}/oauth/introspect`, { token });

    if (!response.data || response.data.status === 'error' || !response.data.data.active) {
      return res.status(401).json({
        status: 'error',
        code: 401,
        message: 'Invalid, expired, or revoked token',
        timestamp: new Date().toISOString(),
        service: 'api-gateway',
      });
    }

    req.user = response.data.data;
    next();

  } catch (err) {
    return res.status(401).json({
      status: 'error',
      code: 401,
      message: 'Authentication service unavailable or invalid token',
      timestamp: new Date().toISOString(),
      service: 'api-gateway',
    });
  }
};

module.exports = verifyToken;