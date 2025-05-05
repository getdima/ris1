import asyncio
import os
from aiohttp import web
from worker import Worker

manager_url = 'http://manager:8080'

async def main():
    worker = Worker(manager_url)

    worker_port = os.getenv("PORT")
    worker_name = os.getenv("WORKER_NAME")

    app = web.Application()
    app.add_routes([web.post('/internal/api/worker/hash/crack/task', worker.handle_execute)])
    app.add_routes([web.get('/healthcheck', worker.handle_healthcheck)])
    app.add_routes([web.get('/progress', worker.handle_progress)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, worker_name, worker_port)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())