from . import config


class Task(dict):
    def __init__(self, **context):
        self.update(context)
        # TODO: validate
        config.TASK_PROFILE
