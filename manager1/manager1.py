import uuid

class QueueManager:
    def __init__ (self, workers_url) :
        self.queue = {}
        self.workers_url = workers_url

    def make_request (self, hash, maxLength):
        if (self.queue.len <= 100) :
            request_id = str(uuid.uuid4())
            self.queue[request_id] = {
                'status' : "NEW",
                'hash' : hash,
                'maxLength' : maxLength,
                'result' : None
            }
            return request_id
        else :
            return None
        
    def get_request (self, request_id) :
        return self.queue.get(request_id)