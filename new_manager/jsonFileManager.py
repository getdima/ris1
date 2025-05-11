import json
import os

class JSONFileManager:
    def __init__(self, base_path, queue_path):
        self.base_path = base_path
        self.queue_path = queue_path

    async def save_queue(self, item, mode):
        if os.path.exists(self.queue_path):
            with open(self.queue_path, 'r') as f:
                dataQueue = json.load(f)

            if (mode == 'put'):
                dataQueue.append(item) 
            if (mode == 'pop'):
                dataQueue.pop(0) 
        
            with open(self.queue_path, 'w') as f:
                json.dump(dataQueue, f)

    def get_base(self):
        if os.path.exists(self.base_path):
            with open(self.base_path, 'r') as f:
                return json.load(f)
        return {}

    async def save_base_to_file(self, data):
        if os.path.exists(self.base_path):
            with open(self.base_path, 'w') as f:
                json.dump(data, f)

    async def get_queue(self):
        if os.path.exists(self.queue_path):
            with open(self.queue_path, 'r') as f:
                return json.load(f)
        return []