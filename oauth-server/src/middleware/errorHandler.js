const { errorResponse } = require('../utils/response');

const errorHandler = (err, req, res, next) => {
  return errorResponse(res, err.code || 500, err.message || 'Server error');
};

module.exports = errorHandler;