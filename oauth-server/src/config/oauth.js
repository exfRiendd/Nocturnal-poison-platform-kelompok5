const OAuth2Server = require('@node-oauth/oauth2-server');
const oauthModel = require('../models/oauthModel');

const oauth = new OAuth2Server({
  model: oauthModel,
  accessTokenLifetime: parseInt(process.env.JWT_EXPIRES_IN || '3600', 10),
  requireClientAuthentication: {
    password: false,
    client_credentials: true,
    refresh_token: false,
  },
});

module.exports = oauth;