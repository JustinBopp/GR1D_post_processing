# post_tasks.py
CALC_TASKS = []
PLOT_TASKS = []

Msun = 1.98847e33

def calc_task(files=None):
    def decorator(func):
        CALC_TASKS.append((func, files or []))
        #print(f"Registered calc task: {func.__name__}")
        return func
    return decorator

def plot_task(files=None):
    def decorator(func):
        PLOT_TASKS.append((func, files or []))
        #print(f"Registered plot task: {func.__name__}")
        return func
    return decorator