const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const pool = require('../config/database');
require('dotenv').config();

const generateAccessToken = (payload) => {
  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: parseInt(process.env.JWT_EXPIRES_IN),
  });
};

const generateRefreshToken = () => {
  return crypto.randomBytes(40).toString('hex');
};

const successResponse = (res, code, data, message) => {
  return res.status(code).json({
    status: 'success',
    code,
    data,
    message,
    timestamp: new Date().toISOString(),
    service: 'oauth-server',
  });
};

const errorResponse = (res, code, message) => {
  return res.status(code).json({
    status: 'error',
    code,
    data: null,
    message,
    timestamp: new Date().toISOString(),
    service: 'oauth-server',
  });
};

// PASSWORD GRANT
const passwordGrant = async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return errorResponse(res, 400, 'Username and password required');
  }

  try {
    const [rows] = await pool.execute(
      'SELECT * FROM citizen_citizens WHERE email = ? OR nik = ?',
      [username, username]
    );

    if (rows.length === 0) {
      return errorResponse(res, 401, 'Invalid credentials');
    }

    const user = rows[0];

    const passwordMatch = await bcrypt.compare(password, user.password);

    if (!passwordMatch) {
      return errorResponse(res, 401, 'Invalid credentials');
    }

    const accessToken = generateAccessToken({
      user_id: user.id,
      email: user.email,
      role: user.role,
    });

    const refreshToken = generateRefreshToken();
    const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    await pool.execute(
      'INSERT INTO oauth_tokens (client_id, user_id, access_token, refresh_token, expires_at) VALUES (?, ?, ?, ?, ?)',
      [null, user.id, accessToken, refreshToken, expiresAt]
    );

    return successResponse(res, 200, {
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: 'Bearer',
      expires_in: parseInt(process.env.JWT_EXPIRES_IN),
    }, 'Login successful');

  } catch (err) {
    return errorResponse(res, 500, 'Server error');
  }
};

// CLIENT CREDENTIALS GRANT
const clientCredentialsGrant = async (req, res) => {
  try {
    const accessToken = generateAccessToken({
      client_id: req.client.client_id,
      role: 'service',
    });

    return successResponse(res, 200, {
      access_token: accessToken,
      token_type: 'Bearer',
      expires_in: parseInt(process.env.JWT_EXPIRES_IN),
    }, 'Token issued');

  } catch (err) {
    return errorResponse(res, 500, 'Server error');
  }
};

// REFRESH TOKEN GRANT
const refreshTokenGrant = async (req, res) => {
  const { refresh_token } = req.body;

  if (!refresh_token) {
    return errorResponse(res, 400, 'Refresh token required');
  }

  try {
    const [rows] = await pool.execute(
      'SELECT * FROM oauth_tokens WHERE refresh_token = ? AND expires_at > NOW()',
      [refresh_token]
    );

    if (rows.length === 0) {
      return errorResponse(res, 401, 'Invalid or expired refresh token');
    }

    const tokenData = rows[0];

    const [userRows] = await pool.execute(
      'SELECT * FROM citizen_citizens WHERE id = ?',
      [tokenData.user_id]
    );

    if (userRows.length === 0) {
      return errorResponse(res, 401, 'User not found');
    }

    const user = userRows[0];

    const newAccessToken = generateAccessToken({
      user_id: user.id,
      email: user.email,
      role: user.role,
    });

    const newRefreshToken = generateRefreshToken();
    const newExpiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);

    await pool.execute(
      'DELETE FROM oauth_tokens WHERE refresh_token = ?',
      [refresh_token]
    );

    await pool.execute(
      'INSERT INTO oauth_tokens (client_id, user_id, access_token, refresh_token, expires_at) VALUES (?, ?, ?, ?, ?)',
      [tokenData.client_id, user.id, newAccessToken, newRefreshToken, newExpiresAt]
    );

    return successResponse(res, 200, {
      access_token: newAccessToken,
      refresh_token: newRefreshToken,
      token_type: 'Bearer',
      expires_in: parseInt(process.env.JWT_EXPIRES_IN),
    }, 'Token refreshed');

  } catch (err) {
    return errorResponse(res, 500, 'Server error');
  }
};

// validasi token
const introspect = async (req, res) => {
  const { token } = req.body;

  if (!token) {
    return errorResponse(res, 400, 'Token required');
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    const [rows] = await pool.execute(
      'SELECT * FROM oauth_tokens WHERE access_token = ?',
      [token]
    );

    if (rows.length === 0) {
      return successResponse(res, 200, { active: false }, 'Token inactive');
    }

    return successResponse(res, 200, {
      active: true,
      user_id: decoded.user_id,
      client_id: decoded.client_id,
      role: decoded.role,
      expires_at: rows[0].expires_at,
    }, 'Token active');

  } catch (err) {
    return successResponse(res, 200, { active: false }, 'Token invalid');
  }
};

// logout
const revoke = async (req, res) => {
  const { token } = req.body;

  if (!token) {
    return errorResponse(res, 400, 'Token required');
  }

  try {
    await pool.execute(
      'DELETE FROM oauth_tokens WHERE access_token = ? OR refresh_token = ?',
      [token, token]
    );

    return successResponse(res, 200, null, 'Token revoked');

  } catch (err) {
    return errorResponse(res, 500, 'Server error');
  }
};

module.exports = {
  passwordGrant,
  clientCredentialsGrant,
  refreshTokenGrant,
  introspect,
  revoke,
};