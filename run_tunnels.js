const localtunnel = require('localtunnel');

async function startTunnel(port, subdomain) {
  const create = async () => {
    try {
      const tunnel = await localtunnel({ port, subdomain });
      console.log(`[OK] Tunnel for port ${port} running at: ${tunnel.url}`);
      tunnel.on('close', () => {
        console.log(`[WARN] Tunnel for port ${port} closed, reconnecting in 2s...`);
        setTimeout(create, 2000);
      });
      tunnel.on('error', (err) => {
        console.error(`[ERR] Tunnel error on port ${port}:`, err.message);
      });
    } catch (e) {
      console.error(`[ERR] Failed to start tunnel for port ${port}:`, e.message);
      setTimeout(create, 3000);
    }
  };
  create();
}

console.log('Starting persistent tunnels for ports 3000 and 8000...');
startTunnel(3000, 'ins-liff-v2-2026');
startTunnel(8000, 'ins-api-v2-2026');
