const client = require('prom-client');

const register = new client.Registry();
client.collectDefaultMetrics({ register });

// request masuk per route, method
const httpRequestCounter = new client.Counter({
  name: 'gateway_http_requests_total',
  help: 'Total HTTP requests received by the gateway',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register],
});

// ukur response time
const httpRequestDuration = new client.Histogram({
  name: 'gateway_http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.05, 0.1, 0.3, 0.5, 1, 2, 5],
  registers: [register],
});

module.exports = { register, httpRequestCounter, httpRequestDuration };