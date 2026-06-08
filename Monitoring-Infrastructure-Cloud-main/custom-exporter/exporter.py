from prometheus_client import start_http_server, Histogram, Counter, Gauge
import requests, time

LATENCY = Histogram(
    'http_request_duration_seconds',
    'Temps de réponse HTTP',
    ['endpoint'],
    buckets=[.05, .1, .25, .5, 1, 2.5, 5]
)
REQUESTS = Counter(
    'http_requests_total',
    'Nombre total de requêtes',
    ['endpoint', 'status_code']
)
AVAILABLE = Gauge('site_availability_up', 'Site disponible (1=ok, 0=down)')
SIZE = Gauge('http_content_size_bytes', 'Taille réponse en octets', ['endpoint'])

PAGES = ['/', '/index.html', '/menu.html']

def probe(endpoint):
    try:
        start = time.time()
        r = requests.get(f'http://nginx:80{endpoint}', timeout=5)
        duration = time.time() - start
        LATENCY.labels(endpoint=endpoint).observe(duration)
        REQUESTS.labels(endpoint=endpoint, status_code=str(r.status_code)).inc()
        SIZE.labels(endpoint=endpoint).set(len(r.content))
        AVAILABLE.set(1)
    except Exception:
        AVAILABLE.set(0)
        REQUESTS.labels(endpoint=endpoint, status_code='timeout').inc()

if __name__ == '__main__':
    start_http_server(9200)
    print("Exporter démarré sur :9200")
    while True:
        for page in PAGES:
            probe(page)
        time.sleep(10)
