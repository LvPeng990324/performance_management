import multiprocessing

bind = "127.0.0.1:8081"
workers = multiprocessing.cpu_count() * 2 + 1
reload = True
daemon = True
errorlog = '/performance_management/logs/gunicorn_error.log'
proc_name = 'gunicorn_performance_management_project'
