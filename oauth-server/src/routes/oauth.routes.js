const express = require('express');
const router = express.Router();
const { tokenHandler, introspectHandler, revokeHandler } = require('../controllers/oauthController');

router.post('/token', tokenHandler);
router.post('/introspect', introspectHandler);
router.post('/revoke', revokeHandler);

module.exports = router;