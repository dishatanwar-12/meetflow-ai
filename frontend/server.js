import { createServer } from 'vite';

async function start() {
  const server = await createServer({
    configFile: './vite.config.ts',
    server: {
      port: 3000,
      host: '0.0.0.0',
    },
  });
  await server.listen();
  console.log('MeetFlow AI frontend running at http://localhost:3000');
}

start().catch((err) => {
  console.error('Failed to start frontend server:', err);
  process.exit(1);
});
