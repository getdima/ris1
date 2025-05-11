import asyncio
import hashlib
import json
import sys
from aiohttp import web
from hashlib import md5
import xml.etree.ElementTree as ET
import aiohttp
import requests

class WorkerExecuter:
    def __init__ (self, manager_url) :
        self.manager_url = manager_url
        self.curr_number = 0;
        self.total = 0; 
        self.results = []

    def num_to_word(self, num, length):
        word = ''

        whole_part = num

        for i in range (1, length + 1):
            whole_part, rem_part = divmod(whole_part, self.alphabet_len)

            char = str(self.alphabet[rem_part])
            word += char

        reversed_text = ''.join(reversed(word))
        return reversed_text

    async def calculate_hash(self, params):
        hash = params['hash']
        maxLength = int(params['maxLength'])
        part_number = int(params['part_number'])
        part_count = int(params['part_count'])
        self.alphabet = params['alphabet']
        self.alphabet_len = len(self.alphabet)

        results = []

        curr_num = 1

        for length in range(1, maxLength + 1):
            self.total += int(self.alphabet_len ** length / part_count)

        for length in range(1, maxLength + 1):
            total_counts = self.alphabet_len ** length

            words_in_part = int(total_counts / part_count)

            start_num = int(words_in_part * part_number)
            end_num = int(words_in_part * (part_number + 1) - 1)

            for word_num in range(start_num, end_num + 1):
                curr_num += 1 

                self.curr_number = curr_num

                word = self.num_to_word(word_num, length)

                md5 = hashlib.md5(word.encode()).hexdigest()
                if md5 == hash:
                    results.append(word)
                    self.results = results
                
                await asyncio.sleep(0)
            curr_num = 0

        return results
    
    def send_response(self, data):
        root = ET.Element('CrackHashWorkerResponse')
        RequestId = ET.SubElement(root, 'RequestId')
        RequestId.text = data['request_id']
        PartNumber = ET.SubElement(root, 'PartNumber')
        PartNumber.text = str(data['part_number'])

        Answers = ET.SubElement(root, 'Answers')
        for res in self.results:
            ET.SubElement(Answers, 'words').text = res

        xml_data = ET.tostring(root).decode()
        headers = {'Content-Type': 'application/xml'}

        response = requests.patch(f"{self.manager_url}/internal/api/manager/hash/crack/request", data=xml_data, headers=headers)

        self.curr_number = 0
        self.total = 0
        self.results = []

class Worker:
    def __init__ (self, manager_url) :
        self.worker_exec = WorkerExecuter(manager_url)

    async def handle_execute(self, request):
        data = await request.json()

        results = await self.worker_exec.calculate_hash(data)
        self.worker_exec.send_response(data)
        # print(results, file=sys.stderr)
 
        return web.Response(text="OK")
    
    async def handle_healthcheck(self, request):
        return web.Response(text="OK")
    
    async def handle_progress(self, request):
        progress = "Ожидает задачу"
        res = []
        if (self.worker_exec.total > 0):
            progress = f'{int((self.worker_exec.curr_number / self.worker_exec.total * 100))}%'

        data = f"Текущий прогресс: {progress}; Текущий результат: {self.worker_exec.results}"
        return web.Response(text=data)