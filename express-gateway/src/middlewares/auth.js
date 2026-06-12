const jwt = require('jsonwebtoken');
require('dotenv').config();

const verifyToken = (req, res, next) => {
  const publicPaths = ['/health', '/metrics', '/oauth/token'];
  
  if (publicPaths.includes(req.path) || (req.path === '/api/citizens' && req.method === 'POST')) {
    return next();
  }

  const authHeader = req.headers['authorization'];

  if (!authHeader || !authHeader.startsWith('Bearer')) {
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
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({
      status: 'error',
      code: 401,
      message: 'Invalid or expired token',
      timestamp: new Date().toISOString(),
      service: 'api-gateway',
    });
  }
};

module.exports = verifyToken;