import os

bind = os.getenv("GUNICORN_BIND") or "0.0.0.0:8080"
worker_class = os.getenv("GUNICORN_WORKER_CLASS") or "gthread"
workers = int(os.getenv("GUNICORN_WORKERS") or 2)
threads = int(os.getenv("GUNICORN_THREADS") or 4)
reload = bool(eval(os.getenv("GUNICORN_RELOAD", "True").title()))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS") or 1500)
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER") or 100)
reload_engine = os.getenv("GUNICORN_RELOAD_ENGINE", "poll")
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "0") == "1"
