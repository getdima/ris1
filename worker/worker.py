import asyncio
import hashlib
import json
import sys
from aiohttp import web
from hashlib import md5
import xml.etree.ElementTree as ET
import aiohttp

class Worker:
    def __init__ (self, manager_url) :
        self.manager_url = manager_url
        self.curr_number = 0;
        self.curr_length = 0;   
        self.result = []
    
    async def get_progress(self):
        progress = {
            "curr_number" : self.curr_number,
            "curr_length" : self.curr_length,
            "result" : self.result
        }
        return progress
        
    # async def set_progress(self, new_values):
    #     async with self.lock:
    #         if ("curr_number" in new_values):
    #             self.curr_number = new_values["curr_number"]
    #         if ("curr_length" in new_values):
    #             self.curr_length = new_values["curr_length"]
    #         if ("result" in new_values):
    #             self.result = new_values["result"]
                    
    
    async def num_to_word(self, num, length):
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

        curr_num = 0

        for length in range(1, maxLength + 1):
            self.curr_length = length

            total_counts = self.alphabet_len ** length

            words_in_part = int(total_counts / part_count)

            start_num = int(words_in_part * part_number)
            end_num = int(words_in_part * (part_number + 1) - 1)

            for word_num in range(start_num, end_num + 1):
                curr_num += 1 

                self.curr_number = curr_num

                word = await self.num_to_word(word_num, length)

                md5 = hashlib.md5(word.encode()).hexdigest()
                if md5 == hash:
                    results.append(word)
                    self.results = results
            curr_num = 0

        return results


    async def handle_execute(self, request):
        data = await request.json()

        results = await self.calculate_hash(data)

        # if (data['part_number'] == 0):
        #     print(results, file=sys.stderr)

        # if (int(data['part_number']) == 0):
        #     while True:
        #         mate = ''
 
        root = ET.Element('CrackHashWorkerResponse')
        RequestId = ET.SubElement(root, 'RequestId')
        RequestId.text = data['request_id']
        PartNumber = ET.SubElement(root, 'PartNumber')
        PartNumber.text = str(data['part_number'])

        Answers = ET.SubElement(root, 'Answers')
        for res in results:
            ET.SubElement(Answers, 'words').text = res

        xml_data = ET.tostring(root).decode()
        headers = {'Content-Type': 'application/xml'}

        async with aiohttp.ClientSession() as session:
            response = await session.patch(f"{self.manager_url}/internal/api/manager/hash/crack/request", data=xml_data, headers=headers)

        self.curr_number = 0
        self.curr_length = 0
        self.result = []

        return web.Response(text="OK")
    
    async def handle_healthcheck(self, request):
        return web.Response(text="OK")
    
    async def handle_progress(self, request):
        progress = await self.get_progress()
        data = f"Текущий номер: {progress['curr_number']}; Текущая длина строки: {progress['curr_length']}; Текущий результат: {str(progress['result'])}"
        return web.Response(text=data)
        

# aaaaaa 0
# aaaaab 1
# aaaaac 2
# aaaaad 3
# aaaaba 4
# aaaabb 5
# aaaabc 6
# aaaabd 7
# b
# c
# d

# aa 1 
# ab 2
# ac 3
# ad 4


# ba 5
# bb 6
# bc 7
# bd 8

# ca 9
# cb 10
# cc 11
# cd 12

# da 13
# db 14
# dc 15 
# dd 16     






