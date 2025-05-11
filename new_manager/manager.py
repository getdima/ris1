import asyncio
from enum import Enum
import json
import os
import sys
import uuid
from aiohttp import ClientSession, web
import aiohttp
from aiologger.loggers.json import JsonLogger
import xml.etree.ElementTree as ET
from sqlalchemy import JSON

from jsonFileManager import JSONFileManager

logger = JsonLogger.with_default_handlers(
            level='DEBUG',
            serializer_kwargs={'ensure_ascii': False},
        )

class Status(Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    PARTIALLY = "PARTIALLY"  
    ERROR = "ERROR"

class RequestsBase:
    def __init__ (self, json_manager) :
        self.requests = {};
        self.lock = asyncio.Lock()
        self.json_manager = json_manager
  
    async def make_request(self, request_id, hash, maxLength, part_count, alplabet):
        async with self.lock:
            self.requests[request_id] = {
                'status' : Status.NEW.value,
                'hash' : hash,
                'maxLength' : maxLength,
                'parts_collected' : 0,
                'part_count' : part_count,
                'result' : [],
                'alphabet' : alplabet
            }
            await self.json_manager.save_base_to_file(self.requests)
            return request_id
    
    async def get_request(self, request_id) :
        async with self.lock:
            return self.requests[request_id]
        
    async def check_exist_request(self, request_id):
        async with self.lock:
            return request_id in self.requests
        
    async def update_request(self, request_id, new_values):
        async with self.lock:
            if (request_id in self.requests):
                item = self.requests[request_id]
                if ("status" in new_values):
                    if (new_values["status"] == Status.IN_PROGRESS.value):
                        item["parts_collected"] = 0
                    item["status"] = new_values["status"]

                if ("result" in new_values):
                    item['parts_collected'] = item['parts_collected'] + 1
                    await logger.info(f'{new_values["result"]}')
                    if (len(new_values["result"]) > 0):
                        for elem in new_values["result"]:
                            item["result"].append(elem)
                        if (item['parts_collected'] != item['part_count']):
                            item["status"] = Status.PARTIALLY.value
                    if (item['parts_collected'] == item['part_count']):
                        item["status"] = Status.READY.value

            await self.json_manager.save_base_to_file(self.requests)

    def set_base(self):
        dataBase = self.json_manager.get_base()
        self.requests = dataBase
        

class Manager:
    def __init__ (self, worker_urls, alplabet) :
        self.worker_urls = worker_urls
        self.workers_count = len(worker_urls)
        self.json_manager = JSONFileManager('resourses/dataBase.json', 'resourses/dataQueue.json')
        self.requests_base = RequestsBase(self.json_manager)
        self.queue = asyncio.Queue(100)
        self.alplabet = alplabet

        self.requests_base.set_base()

        self.worker_configs = []

        for index, element in enumerate(worker_urls):
            worker_config = {
                "part_number" : index,
                "part_count" : self.workers_count,
                'url' : element,
                'alphabet' : alplabet,
                'hash' : None,
                'maxLength' : None,
                'request_id' : None
            }
            self.worker_configs.append(worker_config)
    
    async def handle_make_request(self, request):
        data = await request.json()

        # await logger.info(f'Поступил запрос: {data.hash}')

        response = {
            'request_id' : '',
            'error_code' : '',
            'error_message' : ''
        }

        request_id = str(uuid.uuid4())
        hash = data['hash']
        maxLength = int(data['maxLength'])

        item = {
            'request_id' : request_id,
            'hash' : hash,
            'maxLength' : maxLength
        }

        try:
            self.queue.put_nowait(item)

            await self.json_manager.save_queue(item, 'put')

            response['request_id'] = await self.requests_base.make_request(request_id, hash, maxLength, self.workers_count, self.alplabet)
        except asyncio.QueueFull:
            response['error_message'] = 'Очередь переполнена'
            response['error_code'] = 'full_queue'

        return web.Response(text=json.dumps(response, ensure_ascii=False))
    

    async def handle_check_request(self, request):
        request_id = request.query.get('request_id')

        response = {
            'status' : '',
            'result' : None,
            'error_code' : '',
            'error_message' : '',
            'progress' : ''
        }

        isExist = await self.requests_base.check_exist_request(request_id);
        
        if (isExist):
            item = await self.requests_base.get_request(request_id)

            response['status'] = item['status']
            response['result'] = f"[{', '.join(item['result'])}]"
        else:
            response['error_message'] = 'Запрос с указанным id не существует'
            response['error_code'] = 'request_not_exist'

        return web.Response(text=json.dumps(response, ensure_ascii=False))
    

    async def handle_worker_progress(self, request):

        response = {
            'error_code' : '',
            'error_message' : '',
            'data' : ''
        }

        data = []

        async with aiohttp.ClientSession() as session:
            tasks = [self.task_get_progress(config, session) for config in self.worker_configs]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                data.append(result)

        response['data'] = data
        
        return web.Response(text=json.dumps(response, ensure_ascii=False))
    


    async def handle_patch_request(self, request):
        data = await request.text()
        root = ET.fromstring(data)
        request_id = root.findtext('RequestId')
        results = [elem.text for elem in root.findall('Answers/words')]

        # await logger.info(f'{results}')

        new_value = {
            "result" : results
        }

        await self.requests_base.update_request(request_id, new_value)

        return web.Response(text="OK")
        


    async def execution_requests(self):
        while True:
            try:
                workers_is_ready = True
                item = self.queue.get_nowait()

                new_values = {
                    'status' : Status.IN_PROGRESS.value
                }
                await self.requests_base.update_request(item['request_id'], new_values)

                async with aiohttp.ClientSession() as session:
                    tasks = [self.task_health_check(config, session) for config in self.worker_configs]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in results:
                        if result != 'OK':
                            workers_is_ready = False

                await logger.info(f'workers_is_ready: {workers_is_ready}')

                if (workers_is_ready):
                    for elem in self.worker_configs:
                        elem['hash'] = item['hash']
                        elem['maxLength'] = item['maxLength']
                        elem['request_id'] = item['request_id']

                    async with aiohttp.ClientSession() as session:
                        tasks = [self.task_crack_hash(config, session) for config in self.worker_configs]
                        results = await asyncio.gather(*tasks, return_exceptions=True)

                        for result in results:
                            if result != 'OK':
                                new_values = {
                                    'status' : Status.ERROR.value
                                }
                                await self.requests_base.update_request(item['request_id'], new_values)

                    for elem in self.worker_configs:
                        elem['hash'] = None
                        elem['maxLength'] = None
                        elem['request_id'] = None

                    self.queue.task_done()
                    await self.json_manager.save_queue(None, "pop")
                    await asyncio.sleep(1)
                else:
                    new_values = {
                        'status' : Status.ERROR.value
                    }
                    await self.requests_base.update_request(item['request_id'], new_values)
                    self.queue.task_done()
                    await self.json_manager.save_queue(None, "pop")
                    await asyncio.sleep(15)
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)

    async def start_execution_requests(self, app):
        app['execution_requests'] = asyncio.create_task(self.execution_requests())

    async def fill_queue_form_file(self, app):
        dataQueue = await self.json_manager.get_queue()
        for i in range (0, len(dataQueue)):
            await self.queue.put(dataQueue[i])

    async def task_health_check(self, config, session):
        url = config['url']
        try:
            async with session.get(f"{url}/healthcheck", timeout = 10) as response:
                return 'OK'
        except asyncio.TimeoutError:
            return f"Request to {url} timed out"
        except Exception as e:
            return f"Error fetching {url}: {e}"

    async def task_crack_hash(self, config, session):
        url = config['url']
        try:
            async with session.post(f"{url}/internal/api/worker/hash/crack/task", json=config, timeout = 600) as response:
                return "OK"
        except asyncio.TimeoutError:
            return f"Request to {url} timed out"
        except Exception as e:
            return f"Error fetching {url}: {e}"
    
    async def task_get_progress(self, config, session):
        try:
            async with session.get(f"{config['url']}/progress") as response:
                data = await response.text()
                return f'{config['part_number']}: {data}'
        except asyncio.TimeoutError:
            return f'{config['part_number']}: Error'
        except Exception as e:
            return f'{config['part_number']}: Error'