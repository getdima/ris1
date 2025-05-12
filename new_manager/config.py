WORKER_URLS = ['http://worker1:8081', 'http://worker2:8082', 'http://worker3:8083']
ALPHABET = 'abcdefghijklmnopqrstuvwxyz0123456789'
CRACK_MANAGER_PATH = '/api/hash/crack'
REQUEST_STATUS_PATH = '/api/hash/status'
MANAGER_PATCH_PATH = '/internal/api/manager/hash/crack/request'
ALL_WORKER_PROGRESS_PATH = '/workerProgress'

MANAGER_PORT = 8080
MANAGER_HOST = 'manager'

JSON_BASE_PATH = 'resourses/dataBase.json'
JSON_QUEUE_PATH = 'resourses/dataQueue.json'

WORKER_HEALTH_CHECK_PATH = '/healthcheck'
WORKER_CRACK_TASK_PATH = '/internal/api/worker/hash/crack/task'
WORKER_PROGRESS_PATH = '/progress'
