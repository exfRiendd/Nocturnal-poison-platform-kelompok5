const express = require('express');
const morgan = require('morgan');
const axios = require('axios');
const proxy = require('express-http-proxy');
const dotenv = require('dotenv');
const { globalLimiter } = require('./src/middlewares/rate-limiter');
const proxyRouter = require('./src/routes/proxy');
const { register } = require('./src/config/metrics');
const metricsCollector = require('./src/middlewares/metrics-collector');

dotenv.config();

const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined'));
app.use(metricsCollector);
app.use(globalLimiter);

app.get('/health', async (req, res) => {
  const services = [
    { name: 'citizen-service', url: process.env.CITIZEN_SERVICE_URL },
    { name: 'traffic-service', url: process.env.TRAFFIC_SERVICE_URL },
    { name: 'env-service', url: process.env.ENV_SERVICE_URL },
    { name: 'python-ml', url: process.env.PYTHON_ML_URL },
  ];

  const results = await Promise.allSettled(
    services.map((svc) =>
      axios.get(`${svc.url}/health`, { timeout: 3000 })
        .then(() => ({ name: svc.name, status: 'healthy' }))
        .catch(() => ({ name: svc.name, status: 'unhealthy' }))
    )
  );

  const statuses = results.map((r) => r.value);
  const allHealthy = statuses.every((s) => s.status === 'healthy');

  return res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ok' : 'degraded',
    code: allHealthy ? 200 : 503,
    data: statuses,
    timestamp: new Date().toISOString(),
    service: 'api-gateway',
  });
});

app.get('/metrics', async (req, res) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (err) {
    res.status(500).end(err.message);
  }
});

app.use('/oauth', proxy(process.env.OAUTH_SERVER_URL, {
  proxyReqPathResolver: (req) => {
    return '/oauth' + req.url;
  },
  proxyErrorHandler: (err, res, next) => {
    return res.status(502).json({
      status: 'error',
      code: 502,
      data: null,
      message: 'OAuth server unavailable',
      timestamp: new Date().toISOString(),
      service: 'api-gateway',
    });
  },
}));

app.use('/', proxyRouter);

app.use((req, res) => {
  res.status(404).json({
    status: 'error',
    code: 404,
    data: null,
    message: 'Service not found',
    timestamp: new Date().toISOString(),
    service: 'api-gateway',
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});