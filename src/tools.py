import time

class DClock:
    tasks = {}
    ema_alpha = 0.1
    ema_durations = {}
    min_durations = {}
    max_durations = {}
    execute_counts = {}

    @classmethod
    def start(cls, task_id):
        cls.tasks[task_id] = time.time()

    @classmethod
    def finish(cls, task_id, print_log=False):
        if task_id not in cls.tasks:
            raise ValueError(f"Task '{task_id}' has not been started.")
        
        start_time = cls.tasks.pop(task_id)
        duration = round(time.time() - start_time, 4)
        cls._update_ema(task_id, duration)
        cls._update_min(task_id, duration)
        cls._update_max(task_id, duration)
        cls._update_count(task_id)
        
        if print_log:
            cls.print_log(task_id)

    @classmethod
    def _update_ema(cls, task_id, duration):
        if task_id in cls.ema_durations:
            prev_ema = cls.ema_durations[task_id]
            ema = (1 - cls.ema_alpha) * prev_ema + cls.ema_alpha * duration
        else:
            ema = duration

        cls.ema_durations[task_id] = ema

    @classmethod
    def _update_min(cls, task_id, duration):
        if task_id in cls.min_durations:
            cls.min_durations[task_id] = min(cls.min_durations[task_id], duration)
        else:
            cls.min_durations[task_id] = duration

    @classmethod
    def _update_max(cls, task_id, duration):
        if task_id in cls.max_durations:
            cls.max_durations[task_id] = max(cls.max_durations[task_id], duration)
        else:
            cls.max_durations[task_id] = duration
    
    @classmethod
    def _update_count(cls, task_id):
        if task_id in cls.execute_counts:
            cls.execute_counts[task_id] += 1
        else:
            cls.execute_counts[task_id] = 1

    @classmethod
    def get_average_time(cls, task_id):
        if task_id in cls.ema_durations:
            return round(cls.ema_durations[task_id], 4)
        else:
            return None

    @classmethod
    def get_min_time(cls, task_id):
        if task_id in cls.min_durations:
            return round(cls.min_durations[task_id], 4)
        else:
            return None

    @classmethod
    def get_max_time(cls, task_id):
        if task_id in cls.max_durations:
            return round(cls.max_durations[task_id], 4)
        else:
            return None

    @classmethod
    def get_average_executes_per_second(cls, task_id):
        if task_id in cls.execute_counts and task_id in cls.ema_durations:
            if cls.ema_durations[task_id] == 0:
                return None
            return round(1 / cls.ema_durations[task_id], 2)
        else:
            return None

    @classmethod
    def print_average_time(cls, task_id):
        average_time = cls.get_average_time(task_id)
        if average_time is not None:
            print(f"-----\nAverage time for '{task_id}': {average_time} seconds")
        else:
            print(f"-----\nNo average time available for '{task_id}'")

    @classmethod
    def print_log(cls, task_id):
        average_time = cls.get_average_time(task_id)
        min_time = cls.get_min_time(task_id)
        max_time = cls.get_max_time(task_id)
        avg_executes_per_second = cls.get_average_executes_per_second(task_id)

        if average_time is not None:
            print(f"-----\nTask: '{task_id}'")
            print(f"Average time: {average_time} seconds")
            print(f"Minimum time: {min_time} seconds")
            print(f"Maximum time: {max_time} seconds")
            print(f"Average executes per second: {avg_executes_per_second}")
        else:
            print(f"-----\nNo log available for task '{task_id}'")
