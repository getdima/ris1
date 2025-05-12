import asyncio
import os
from aiohttp import web
from worker import Worker
from config import *


async def main():
    worker = Worker(MANAGER_URL)

    worker_port = os.getenv(WORKER_PORT_ENV_PATH)
    worker_name = os.getenv(WORKER_NAME_ENV_PATH)

    app = web.Application()
    app.add_routes([web.post(WORKER_CRACK_TASK_PATH, worker.handle_execute)])
    app.add_routes([web.get(WORKER_HEALTH_CHECK_PATH, worker.handle_healthcheck)])
    app.add_routes([web.get(WORKER_PROGRESS_PATH, worker.handle_progress)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, worker_name, worker_port)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())