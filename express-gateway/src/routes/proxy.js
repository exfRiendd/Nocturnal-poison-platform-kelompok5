const express = require('express');
const proxy = require('express-http-proxy');
const routesConfig = require('../config/gateway-config');
const router = express.Router();

routesConfig.forEach((route) => {
  router.use(route.prefix, proxy(route.target, {
    proxyReqPathResolver: (req) => {
      if (route.targetPrefix) {
        const subPath = req.url === '/' ? '' : req.url;
        return (route.targetPrefix + subPath).replace(/\/+/g, '/');
      }

      let resolvedPath = route.stripPrefix
        ? req.url
        : req.originalUrl;

      if (!resolvedPath.startsWith('/')) {
        resolvedPath = '/' + resolvedPath;
      }

      return resolvedPath;
    },
    proxyErrorHandler: (err, res, next) => {
      return res.status(502).json({
        status: 'error',
        code: 502,
        data: null,
        message: `Bad gateway. Target service for ${route.prefix} is unavailable.`,
        timestamp: new Date().toISOString(),
        service: 'api-gateway',
      });
    }
  }));
});

module.exports = router;