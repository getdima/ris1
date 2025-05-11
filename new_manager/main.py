import asyncio
from aiohttp import web
from manager import Manager

worker_urls = ['http://worker1:8081', 'http://worker2:8082', 'http://worker3:8083']
alplabet = 'abcdefghijklmnopqrstuvwxyz0123456789'

async def main():
    manager = Manager(worker_urls, alplabet)
    app = web.Application()
    app.add_routes([web.post('/api/hash/crack', manager.handle_make_request)])
    app.add_routes([web.get('/api/hash/status', manager.handle_check_request)])
    app.add_routes([web.patch('/internal/api/manager/hash/crack/request', manager.handle_patch_request)])
    app.add_routes([web.get('/workerProgress', manager.handle_worker_progress)])

    app.on_startup.append(manager.start_execution_requests)
    app.on_startup.append(manager.fill_queue_form_file)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'manager', 8080)
    await site.start()

    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())