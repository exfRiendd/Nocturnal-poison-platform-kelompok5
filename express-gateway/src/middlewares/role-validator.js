const roleValidator = (req, res, next) => {
  if (!req.user) {
    return next();
  }

  const role = req.user.role;
  const method = req.method;
  const path = req.path;

  const adminOnlyRoutes = [
    { p: '/api/zones', m: ['POST', 'PUT', 'DELETE'] },
    { p: '/api/alerts', m: ['POST', 'PUT', 'DELETE'] }
  ];

  //Admin
  for (let r of adminOnlyRoutes) {
    if (path.startsWith(r.p) && r.m.includes(method)) {
      if (role !== 'admin') {
        return res.status(403).json({
          status: 'error',
          code: 403,
          message: 'Access Denied: Admin privileges required',
          service: 'api-gateway'
        });
      }
    }
  }

  // GET /api/citizens (tanpa ID) hanya untuk Admin
  if ((path === '/api/citizens' || path === '/api/citizens/') && method === 'GET') {
    if (role !== 'admin') {
      return res.status(403).json({
        status: 'error',
        code: 403,
        message: 'Access Denied: Admin privileges required to view all citizens',
        service: 'api-gateway'
      });
    }
  }

  // Citizen
  const citizenOnlyRoutes = [
    { p: '/api/activity-sessions', m: ['POST'] },
    { p: '/api/reports', m: ['POST'] },
    { p: '/api/notifications', m: ['GET', 'PATCH'] },
    { p: '/api/citizens/exposures', m: ['GET'] },
    { p: '/predict/lung-impact', m: ['POST'] },
    { p: '/predict/full-exposure', m: ['POST'] },
    { p: '/predict/toxic-dose', m: ['POST'] }
  ];

  for (let r of citizenOnlyRoutes) {
    if (path.startsWith(r.p) && r.m.includes(method)) {
      if (role !== 'citizen') {
        return res.status(403).json({
          status: 'error',
          code: 403,
          message: 'Access Denied: Citizen privileges required',
          service: 'api-gateway'
        });
      }
    }
  }

  next();
};

module.exports = roleValidator;
