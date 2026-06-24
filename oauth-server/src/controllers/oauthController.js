const OAuth2Server = require('@node-oauth/oauth2-server');
const { Request, Response } = OAuth2Server;
const oauth = require('../config/oauth');
const oauthModel = require('../models/oauthModel');
const { successResponse, errorResponse } = require('../utils/response');

const tokenHandler = async (req, res, next) => {
  if (!req.body.client_id) {
    return errorResponse(res, 400, 'client_id is required');
  }

  try {
    const token = await oauth.token(new Request(req), new Response(res));
    return successResponse(res, 200, {
      access_token: token.accessToken,
      refresh_token: token.refreshToken,
      token_type: 'Bearer',
      expires_in: Math.floor((new Date(token.accessTokenExpiresAt) - new Date()) / 1000),
    }, 'Token issued');
  } catch (err) {
    return next(err);
  }
};

const introspectHandler = async (req, res, next) => {
  const { token } = req.body;
  if (!token) return errorResponse(res, 400, 'Token required');

  try {
    const accessToken = await oauthModel.getAccessToken(token);

    if (!accessToken || new Date(accessToken.accessTokenExpiresAt) < new Date()) {
      return successResponse(res, 200, { active: false }, 'Token inactive');
    }

    return successResponse(res, 200, {
      active: true,
      user_id: accessToken.user?.id ?? null,
      client_id: accessToken.client?.id ?? null,
      role: accessToken.user?.role ?? null,
      expires_at: accessToken.accessTokenExpiresAt,
    }, 'Token active');
  } catch (err) {
    return next(err);
  }
};

const revokeHandler = async (req, res, next) => {
  const { token } = req.body;
  if (!token) return errorResponse(res, 400, 'Token required');

  try {
    await oauthModel.revokeToken({ accessToken: token, refreshToken: token });
    return successResponse(res, 200, null, 'Token revoked');
  } catch (err) {
    return next(err);
  }
};

module.exports = { tokenHandler, introspectHandler, revokeHandler };