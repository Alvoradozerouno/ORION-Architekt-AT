"""
Gunicorn Production Configuration
==================================
Optimized for production deployment with ORION Architekt-AT API

Author: ORION Engineering Team
Date: 2026-04-11
Status: PRODUCTION READY
"""

import multiprocessing
import os

# ============================================================================
# Server Socket
# ============================================================================
bind = "0.0.0.0:8000"
backlog = 2048

# ============================================================================
# Worker Processes
# ============================================================================
# Workers = (2 x CPU cores) + 1
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Worker class - use uvicorn for async support
worker_class = "uvicorn.workers.UvicornWorker"

# Worker connections (for async workers)
worker_connections = 1000

# Maximum requests per worker before restart (prevents memory leaks)
max_requests = 1000
max_requests_jitter = 100

# ============================================================================
# Worker Timeouts
# ============================================================================
timeout = 120  # 2 minutes for long-running calculations
graceful_timeout = 30
keepalive = 5

# ============================================================================
# Logging
# ============================================================================
accesslog = "-"  # stdout
errorlog = "-"  # stderr
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Capture output from workers
capture_output = True

# ============================================================================
# Process Naming
# ============================================================================
proc_name = "orion-api"

# ============================================================================
# Server Mechanics
# ============================================================================
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# ============================================================================
# SSL (if terminating SSL at application level)
# ============================================================================
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# ============================================================================
# Server Hooks
# ============================================================================


def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 ORION Architekt-AT API starting...")


def on_reload(server):
    """Called when the server is reloaded."""
    server.log.info("🔄 Server reloading...")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("✅ ORION Architekt-AT API ready to serve requests")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Worker class: {worker_class}")
    server.log.info(f"Listening on: {bind}")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.debug(f"Forking worker #{worker}")


def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker {worker.pid} spawned")


def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forking new master process")


def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info(f"Worker {worker.pid} received INT or QUIT signal")


def worker_abort(worker):
    """Called when a worker is killed by a timeout."""
    worker.log.warning(f"Worker {worker.pid} aborted (timeout)")


def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.debug(f"{req.method} {req.path}")


def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    worker.log.debug(f"{req.method} {req.path} → {resp.status}")


def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker {worker.pid} exited")


def worker_exit(server, worker):
    """Called when a worker is exiting."""
    server.log.info(f"Worker {worker.pid} is exiting")


def nworkers_changed(server, new_value, old_value):
    """Called when the number of workers changes."""
    server.log.info(f"Number of workers changed from {old_value} to {new_value}")


def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("🛑 ORION Architekt-AT API shutting down...")


# ============================================================================
# Environment Variables
# ============================================================================

# Load .env file if exists (development)
raw_env = [
    f"ENVIRONMENT={os.getenv('ENVIRONMENT', 'production')}",
]
