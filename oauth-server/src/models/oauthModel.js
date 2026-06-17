const pool = require('../config/database');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
require('dotenv').config();


const getClient = async (clientId, clientSecret) => {
  const [rows] = await pool.execute(
    'SELECT * FROM oauth_clients WHERE client_id = ?',
    [clientId]
  );
  if (rows.length === 0) return null;

  const client = rows[0];

  // clientSecret dicek kalau dikirim (client_credentials)
  if (clientSecret && client.client_secret !== clientSecret) return null;

  return {
    id: client.client_id, 
    clientId: client.client_id, 
    grants: client.grant_types ? client.grant_types.split(',') : [],
  };
};

const getUser = async (username, password) => {
  const [rows] = await pool.execute(
    'SELECT * FROM citizen_citizens WHERE email = ? OR nik = ?',
    [username, username]
  );
  if (rows.length === 0) return null;

  const user = rows[0];
  const match = await bcrypt.compare(password, user.password);
  return match ? { id: user.id, email: user.email, role: user.role } : null;
};

const generateAccessToken = async (client, user) => {
  const payload = {
    user_id: user ? user.id : null,
    client_id: client.clientId,
    role: user ? user.role : 'service',
  };

  return jwt.sign(payload, process.env.JWT_SECRET, {
    expiresIn: parseInt(process.env.JWT_EXPIRES_IN || '3600', 10),
  });
};

const generateRefreshToken = async () => {
  return crypto.randomBytes(40).toString('hex');
};

const saveToken = async (token, client, user) => {
  await pool.execute(
    'INSERT INTO oauth_tokens (client_id, user_id, access_token, refresh_token, expires_at) VALUES (?, ?, ?, ?, ?)',
    [
      client.clientId,
      user ? user.id : null,
      token.accessToken,
      token.refreshToken || null,
      token.accessTokenExpiresAt,
    ]
  );

  return {
    accessToken: token.accessToken,
    accessTokenExpiresAt: token.accessTokenExpiresAt,
    refreshToken: token.refreshToken,
    refreshTokenExpiresAt: token.refreshTokenExpiresAt,
    client,
    user,
  };
};

const getAccessToken = async (accessToken) => {
  const [rows] = await pool.execute(
    'SELECT * FROM oauth_tokens WHERE access_token = ?',
    [accessToken]
  );
  if (rows.length === 0) return null;
  const row = rows[0];

  try {
    const decoded = jwt.verify(accessToken, process.env.JWT_SECRET);

    return {
      accessToken: row.access_token,
      accessTokenExpiresAt: new Date(row.expires_at),
      client: { id: decoded.client_id },
      user: decoded.user_id ? { id: decoded.user_id, role: decoded.role } : null,
    };
  } catch (err) {
    return null; 
  }
};

const getRefreshToken = async (refreshToken) => {
  const [rows] = await pool.execute(
    `SELECT t.*, c.role FROM oauth_tokens t
     LEFT JOIN citizen_citizens c ON c.id = t.user_id
     WHERE t.refresh_token = ? AND t.expires_at > NOW()`,
    [refreshToken]
  );
  if (rows.length === 0) return null;
  const row = rows[0];

  return {
    refreshToken: row.refresh_token,
    refreshTokenExpiresAt: new Date(row.expires_at),
    client: { id: row.client_id },
    user: row.user_id ? { id: row.user_id, role: row.role } : null,
  };
};

const revokeToken = async (token) => {
  const targetToken = token.refreshToken || token.accessToken;
  await pool.execute(
    'DELETE FROM oauth_tokens WHERE refresh_token = ? OR access_token = ?',
    [targetToken, targetToken]
  );
  return true;
};

module.exports = {
  getClient, getUser, saveToken, getAccessToken, getRefreshToken,
  revokeToken, generateAccessToken, generateRefreshToken,
};