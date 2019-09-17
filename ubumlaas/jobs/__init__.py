import variables as v
from rq import Worker
import multiprocessing as mp


class WorkerBuilder():

    name = None
    queues = {v.q}
    worker = None

    def set_name(self, name):
        self.name = name
        return self

    def set_queue(self, queue):
        self.queues = {queue}
        return self

    def add_queue(self, queue):
        self.queues.add(queue)
        return self

    def create(self):
        if self.name is None:
            self.name = "Worker "+str(v.workers)
        v.workers += 1
        self.worker = Worker(self.queues, connection=v.r, name=self.name)
        return self

    def start(self):
        mp.Process(target=self.worker.work).start()
