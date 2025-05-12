import asyncio
from aiohttp import web
from manager import Manager
from config import *


async def main():
    manager = Manager(WORKER_URLS, ALPHABET)
    app = web.Application()
    app.add_routes([web.post(CRACK_MANAGER_PATH, manager.handle_make_request)])
    app.add_routes([web.get(REQUEST_STATUS_PATH, manager.handle_check_request)])
    app.add_routes([web.patch(MANAGER_PATCH_PATH, manager.handle_patch_request)])
    app.add_routes([web.get(ALL_WORKER_PROGRESS_PATH, manager.handle_worker_progress)])

    app.on_startup.append(manager.start_execution_requests)
    app.on_startup.append(manager.fill_queue_form_file)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, MANAGER_HOST, MANAGER_PORT)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())