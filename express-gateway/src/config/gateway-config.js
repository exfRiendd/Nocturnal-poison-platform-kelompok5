require('dotenv').config();

const routes = [
  {
    prefix: '/api/citizens',
    target: process.env.CITIZEN_SERVICE_URL,
  },
  {
    prefix: '/api/traffic',
    target: process.env.TRAFFIC_SERVICE_URL,
  },
  {
    prefix: '/api/environment',
    target: process.env.ENV_SERVICE_URL,
  },
  {
    prefix: '/predict',
    target: process.env.PYTHON_ML_URL,
  },
  {
    prefix: '/detect',
    target: process.env.PYTHON_ML_URL,
  },
  {
    prefix: '/iot',
    target: process.env.PYTHON_ML_URL,
  },
];

module.exports = routes;