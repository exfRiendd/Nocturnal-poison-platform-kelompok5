const pool = require('../config/database');

const validateClient = async (req, res, next) => {
  const { grant_type, client_id, client_secret } = req.body;

  if (grant_type === 'password') {
    return next();
  }

  if (!client_id || !client_secret) {
    return res.status(401).json({
      status: 'error',
      code: 401,
      data: null,
      message: 'Client credentials required',
      timestamp: new Date().toISOString(),
      service: 'oauth-server',
    });
  }

  try {
    const [rows] = await pool.execute(
      'SELECT * FROM oauth_clients WHERE client_id = ?',
      [client_id]
    );

    if (rows.length === 0 || rows[0].client_secret !== client_secret) {
      return res.status(401).json({
        status: 'error',
        code: 401,
        data: null,
        message: 'Invalid client credentials',
        timestamp: new Date().toISOString(),
        service: 'oauth-server',
      });
    }

    req.client = rows[0];
    next();
  } catch (err) {
    return res.status(500).json({
      status: 'error',
      code: 500,
      data: null,
      message: 'Server error',
      timestamp: new Date().toISOString(),
      service: 'oauth-server',
    });
  }
};

module.exports = validateClient;