import variables as v
from rq import Worker
import multiprocessing as mp


class WorkerBuilder():
    """RQ Worker Builder
    """

    name = None
    queues = set()
    worker = None
    proc = None

    def set_name(self, name):
        """Add name to identify worker

        Arguments:
            name {str} -- worker name

        Returns:
            WorkerBuilder -- self
        """
        self.name = name
        return self

    def set_queue(self, queue):
        """Override queues set with unique queue.

        Arguments:
            queue {rq.Queue} -- Queue to add to worker

        Returns:
            WorkerBuilder -- self
        """
        self.queues = {queue}
        return self

    def add_queue(self, queue):
        """Add new queue to worker

        Arguments:
            queue {rq.Queue} -- Queue to add to worker

        Returns:
            WorkerBuilder -- self
        """
        self.queues.add(queue)
        return self

    def create(self):
        """Create a worker object with current configuration.

        Returns:
            WorkerBuilder -- self
        """
        if self.name is None:
            self.name = "UBUMLaaS Worker n:"+str(v.workers)
        v.workers += 1
        self.worker = Worker(self.queues, connection=v.r, name=self.name)
        self.proc = mp.Process(target=self.worker.work, daemon=True)
        return self

    def start(self):
        """Start a new process with the worker.

        Returns:
            WorkerBuilder -- self
        """
        self.proc.start()
        return self

    def kill(self):
        """Kill a process with the worker

        Returns:
            WorkerBuilder -- self
        """
        self.proc.kill()
        return self
