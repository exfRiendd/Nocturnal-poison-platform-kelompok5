require('dotenv').config();

const routes = [
  // PHP-CITIZEN SERVICE 
  { 
    prefix: '/api/citizens',          
    target: process.env.CITIZEN_SERVICE_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/api/reports',           
    target: process.env.CITIZEN_SERVICE_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/api/notifications',     
    target: process.env.CITIZEN_SERVICE_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/api/activity-sessions', 
    target: process.env.CITIZEN_SERVICE_URL, 
    stripPrefix: false 
  },

  // PHP-ENVIRONMENT SERVICE 
  { 
    prefix: '/api/readings',          
    target: process.env.ENV_SERVICE_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/api/alerts',            
    target: process.env.ENV_SERVICE_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/api/zones',             
    target: process.env.ENV_SERVICE_URL, 
    stripPrefix: false 
  },

  // PYTHON-ML SERVICE (Anggota 4)
  { 
    prefix: '/predict',               
    target: process.env.PYTHON_ML_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/detect',                
    target: process.env.PYTHON_ML_URL, 
    stripPrefix: false 
  },
  { 
    prefix: '/context',               
    target: process.env.PYTHON_ML_URL, 
    stripPrefix: false 
  },
];

module.exports = routes;