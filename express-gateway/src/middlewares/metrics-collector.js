const { httpRequestCounter, httpRequestDuration } = require('../config/metrics');

const metricsCollector = (req, res, next) => {
  const end = httpRequestDuration.startTimer();

  res.on('finish', () => {
    const route = req.route?.path || req.path || 'unknown';
    const labels = {
      method: req.method,
      route: route,
      status_code: res.statusCode,
    };
    httpRequestCounter.inc(labels);
    end(labels);
  });

  next();
};

module.exports = metricsCollector;