import os
config = {
    "DEBUG": True,          # some Flask specific configs
    'SECRET_KEY':os.getenv('SECRET_KEY'),
    'CELERY':{
            'broker_url':"redis://redis:6379/0",
            'result_backend':"redis://redis:6379/0",
            'task_ignore_result':False,
            'task_track_started':True,
            'worker_pool':'solo',
            # Flower-specific settings
            'worker_send_task_events': True,  # Enable real-time task monitoring
            'task_track_started': True,  # Track task start time
        },
}
