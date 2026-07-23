/**
 * Solomon JS Proxy
 * Location: /srv/storage/toshiba/BubblePath/codexia-web/solomon-proxy.js
 * Exposes port: 7420
 * Validates SOLOMON_ACTIONS_API_KEY and proxies securely to Solomon API Gateway on port 18789.
 */

const http = require('http');
const crypto = require('crypto');

// Load configurations from environment variables
const PORT = process.env.SOLOMON_PROXY_PORT || 7420;
const BACKEND_BASE_URL = process.env.SOLOMON_API_BASE_URL || 'http://127.0.0.1:18789';
const ACTIONS_API_KEY = process.env.SOLOMON_ACTIONS_API_KEY || 'DEMO_KEY';

// Safe constant-time string comparison helper to prevent timing attacks
function timingSafeEqual(a, b) {
    try {
        const bufA = Buffer.from(a, 'utf-8');
        const bufB = Buffer.from(b, 'utf-8');
        if (bufA.length !== bufB.length) {
            return false;
        }
        return crypto.timingSafeEqual(bufA, bufB);
    } catch (e) {
        return false;
    }
}

function verifyAuth(req) {
    const authHeader = req.headers['authorization'] || '';
    if (!authHeader.startsWith('Bearer ')) {
        return false;
    }
    const token = authHeader.substring(7).trim();
    return timingSafeEqual(token, ACTIONS_API_KEY);
}

const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
    const pathname = url.pathname;

    console.log(`[Proxy] Incoming request: ${req.method} ${pathname}`);

    // CORS & Base headers
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Headers', 'Authorization, Content-Type');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');

    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }

    // Public /api/health
    if (pathname === '/api/health' && req.method === 'GET') {
        // Ping backend api /api/health
        const backendUrl = `${BACKEND_BASE_URL}/api/health`;
        console.log(`[Proxy] Forwarding public health request to: ${backendUrl}`);

        http.get(backendUrl, { timeout: 3000 }, (backendRes) => {
            let data = '';
            backendRes.on('data', chunk => data += chunk);
            backendRes.on('end', () => {
                res.writeHead(backendRes.statusCode);
                res.end(data);
            });
        }).on('error', (err) => {
            console.error('[Proxy] Health forwarding failed:', err.message);
            res.writeHead(502);
            res.end(JSON.stringify({
                ok: false,
                service: 'solomon-proxy',
                status: 'DEGRADED',
                error: 'Backend API is unreachable.'
            }));
        });
        return;
    }

    // Protected Routes
    const protectedRoutes = [
        '/api/command-center/status',
        '/api/command-center/bridge-status',
        '/api/command-center/solomon-chat',
        '/api/command-center/worker-report',
        '/api/command-center/review',
        '/api/command-center/cards',
        '/api/command-center/worker-modes'
    ];

    if (protectedRoutes.includes(pathname)) {
        if (!verifyAuth(req)) {
            console.warn('[Proxy] Authentication failed for protected route');
            res.writeHead(401);
            res.end(JSON.stringify({ ok: false, error: 'Unauthorized' }));
            return;
        }

        // Setup proxy forwarding to backend
        const backendEndpoint = `${BACKEND_BASE_URL}${pathname}${url.search}`;
        console.log(`[Proxy] Authorized. Forwarding request to: ${backendEndpoint}`);

        const parsedBackendUrl = new URL(backendEndpoint);
        const options = {
            hostname: parsedBackendUrl.hostname,
            port: parsedBackendUrl.port,
            path: parsedBackendUrl.pathname + parsedBackendUrl.search,
            method: req.method,
            headers: {
                'Authorization': `Bearer ${ACTIONS_API_KEY}`,
                'Content-Type': 'application/json',
                'X-Request-Id': req.headers['x-request-id'] || ''
            },
            timeout: 10000 // 10-second connect timeout
        };

        const proxyReq = http.request(options, (proxyRes) => {
            res.writeHead(proxyRes.statusCode, proxyRes.headers);
            proxyRes.pipe(res);
        });

        proxyReq.on('error', (err) => {
            console.error('[Proxy] Forwarding error:', err.message);
            res.writeHead(502);
            res.end(JSON.stringify({
                ok: false,
                error: 'Bad Gateway: Backend API service is unavailable or returned error.'
            }));
        });

        req.pipe(proxyReq);
        return;
    }

    // 404 Route Not Found
    res.writeHead(404);
    res.end(JSON.stringify({ ok: false, error: 'Route not found' }));
});

// Run server if started directly
if (require.main === module) {
    server.listen(PORT, '0.0.0.0', () => {
        console.log(`[Proxy] Solomon JS Proxy listening on port ${PORT}`);
        console.log(`[Proxy] Backend endpoint set to: ${BACKEND_BASE_URL}`);
    });
}

module.exports = server;
