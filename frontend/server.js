import { createServer } from 'vite';

async function start() {
  const server = await createServer({
    configFile: './vite.config.ts',
    server: {
      port: 5173,
      host: '0.0.0.0',
    },
  });
  await server.listen();
  console.log('MeetFlow AI frontend server running at http://localhost:5173');
}

start().catch((err) => {
  console.error('Failed to start frontend server:', err);
  process.exit(1);
});
