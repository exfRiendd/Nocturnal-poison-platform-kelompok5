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

module.exports = { successResponse, errorResponse };