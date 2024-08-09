from celery import Celery

from app.core.config import settings

# Initialize Celery app with Redis as both broker and backend
celery_app = Celery("llm_tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

# Configure task routing: all tasks from app.tasks will go to the 'llm_tasks' queue
celery_app.conf.task_routes = {"app.tasks.*": {"queue": "llm_tasks"}}

# Set up a thread pool executor for running async code
# This is useful for I/O-bound tasks
celery_app.conf.task_pool = "threads"

# Use the 'prefork' pool as the main worker pool
# This is the default and is good for general purpose and CPU-bound tasks
celery_app.conf.worker_pool = "prefork"

# Set the number of worker threads/processes
# This determines how many tasks can be executed concurrently
celery_app.conf.worker_concurrency = settings.CELERY_WORKER_CONCURRENCY

# Auto-discover tasks in the specified packages
# This will look for a 'tasks.py' file in the app.core directory
celery_app.autodiscover_tasks(["app.core"])
