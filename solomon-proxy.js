const http = require('http');
const httpProxy = require('http'); // We will use standard http request forwarding for simplicity, zero external deps!
const crypto = require('crypto');

const PORT = process.env.PROXY_PORT || 7420;
const BACKEND_URL = 'http://localhost:18789';
const API_KEY = process.env.SOLOMON_ACTIONS_API_KEY || 'default_secret_key';

function constantTimeCompare(a, b) {
    const aHash = crypto.createHash('sha256').update(a).digest();
    const bHash = crypto.createHash('sha256').update(b).digest();
    return crypto.timingSafeEqual(aHash, bHash);
}

const server = http.createServer((req, res) => {
    // 1. Authenticate Request
    const authHeader = req.headers['authorization'];
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Unauthorized: Missing or malformed Bearer Token' }));
        return;
    }

    const token = authHeader.substring(7);
    if (!constantTimeCompare(token, API_KEY)) {
        res.writeHead(403, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Forbidden: Invalid API Key' }));
        return;
    }

    // 2. Forward/Proxy Request to Flask on port 18789
    const options = {
        hostname: 'localhost',
        port: 18789,
        path: req.url,
        method: req.method,
        headers: req.headers
    };

    const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res, { end: true });
    });

    req.pipe(proxyReq, { end: true });

    proxyReq.on('error', (err) => {
        console.error('[Proxy Error]:', err);
        res.writeHead(502, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Bad Gateway: Backend server is unreachable', details: err.message }));
    });
});

server.listen(PORT, () => {
    console.log(`[Proxy] Edge proxy listening on port ${PORT}, forwarding to ${BACKEND_URL}`);
});
