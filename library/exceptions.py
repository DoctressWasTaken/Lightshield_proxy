class LimitBlocked(Exception):

    def __init__(self, retry_after=1):
        self.retry_after = retry_after
