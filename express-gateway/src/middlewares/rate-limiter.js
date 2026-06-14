const rateLimit = require('express-rate-limit');

const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 menit
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    status: 'error',
    code: 429,
    message: 'Too many requests, please try again later',
    timestamp: new Date().toISOString(),
    service: 'api-gateway',
  },
});

const authLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 jam
  max: 500,
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => req.headers.authorization || req.ip,
  message: {
    status: 'error',
    code: 429,
    message: 'Token rate limit exceeded',
    timestamp: new Date().toISOString(),
    service: 'api-gateway',
  },
});

module.exports = { globalLimiter, authLimiter };