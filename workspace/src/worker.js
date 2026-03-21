const json = (payload, init = {}) =>
  new Response(JSON.stringify(payload, null, 2), {
    status: init.status ?? 200,
    headers: {
      "content-type": "application/json; charset=UTF-8",
      ...(init.headers ?? {}),
    },
  });

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/healthz") {
      return json({
        ok: true,
        service: "opengpt-live",
        status: "healthy",
        timestamp: new Date().toISOString(),
      });
    }

    return json({
      service: "opengpt-live",
      status: "running",
      endpoints: ["/", "/healthz"],
      timestamp: new Date().toISOString(),
    });
  },
};
