import os
from manager1 import QueueManager
from flask import Flask, jsonify

app = Flask(__name__)

worker_urls = ['http://ris1-worker-1:8080', 'http://ris1-worker-2:8080', 'http://ris1-worker-3:8080']

queue_manager = QueueManager(worker_urls)

@app.route('/', methods=['POST'])
def test(request):
    response = {
        'request_id' : '',
        'error_code' : 'test',
        'error_message' : 'Проверка'
    }

    return jsonify(response)

@app.route('/api/hash/crack', methods=['POST'])
def make_request(request):
    data = request.json;

    request_id = queue_manager.make_request(data.hash, data.maxLength)

    response = {
        'request_id' : '',
        'error_code' : '',
        'error_message' : ''
    }

    if (request_id != None):
        response['request_id'] = request_id
    else :
        response['error_code'] = 'full_queue'
        response['error_message'] = 'Очередь переполнена'

    return jsonify(response)

@app.route('/api/hash/status/<string:requestId>', methods=['GET'])
def check_request(request, requestId):
    request = queue_manager.get_request(requestId)

    response = {
        'status' : '',
        'data' : None,
        'error_code' : '',
        'error_message' : ''
    }

    if (response != None):
        response['status'] = response.status
        response['data'] = response.data
    else :
        response['error_code'] = 'request_not_exist'
        response['error_message'] = 'Запрос с указанным id не существует'

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)