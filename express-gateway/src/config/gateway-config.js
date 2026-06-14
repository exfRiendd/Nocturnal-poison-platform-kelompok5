require('dotenv').config();

const routes = [
  {
    prefix: '/api/citizens',
    target: process.env.CITIZEN_SERVICE_URL,
    stripPrefix: true
  },
  {
    prefix: '/api/traffic',
    target: process.env.TRAFFIC_SERVICE_URL,
    stripPrefix: true
  },
  {
    prefix: '/api/environment',
    target: process.env.ENV_SERVICE_URL,
    stripPrefix: true
  },

  {
    prefix: '/predict',
    target: process.env.PYTHON_ML_URL,
    stripPrefix: false
  }
];

module.exports = routes;