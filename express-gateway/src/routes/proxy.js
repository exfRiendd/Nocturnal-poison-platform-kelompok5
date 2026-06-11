const express = require('express');
const proxy = require('express-http-proxy');
const router = express.Router();
const routes = require('../config/gateway-config');
const verifyToken = require('../middlewares/auth');
const { authLimiter } = require('../middlewares/rate-limiter');

routes.forEach((route) => {
  router.use(
    route.prefix,
    verifyToken,
    authLimiter,
    proxy(route.target, {
        proxyReqPathResolver: (req) => {
        return req.url;
      },
      proxyErrorHandler: (err, res, next) => {
        return res.status(502).json({
          status: 'error',
          code: 502,
          data: null,
          message: 'Upstream service unavailable',
          timestamp: new Date().toISOString(),
          service: 'api-gateway',
        });
      },
    })
  );
});

module.exports = router;