from multiprocessing import Queue, Process
from multiprocessing.managers import BaseManager
from queue import Empty
from time import time
from core.agent import Agent
from config import AGENT_MAX_SEARCH_SECS, AGENT_SEC_THRESHOLD


def worker(queue, agent, board, color):
    agent.start(board, color)
    best_move = None
    next_best_move = None
    done_search = False

    while not done_search:
        next_best_move, done_search = agent.find_next_best_move()
        best_move = next_best_move or best_move
        if best_move or done_search:
            print("yield", best_move, done_search)
            queue.put((best_move, done_search))


class AgentManager(BaseManager):
    pass

AgentManager.register("Agent", Agent)


class AgentOperator:

    def __init__(self):
        manager = AgentManager()
        manager.start()
        self._agent = manager.Agent()
        self._agent_manager = None
        self._queue = Queue()
        self._thread = None
        self._time = time()
        self._move = None
        self._done = False

    @property
    def time(self):
        return self._time

    @property
    def done(self):
        return self._done

    def _clear_queue(self):
        while self._queue.qsize():
            self._queue.get()
            self._queue.task_done()

    def start_search(self, board, color):
        if self._thread:
            self._thread = None

        queue = Queue()
        self._queue = queue

        thread = Process(target=worker, args=(queue, self._agent, board, color))
        thread.daemon = True
        thread.start()
        self._thread = thread

        self._time = time()
        self._move = None
        self._done = False

        return thread

    def stop_search(self):
        self._agent.interrupt()
        self._thread.join()

    def update(self):
        if self._done:
            best_move = self._move
            is_search_complete = self._done
        else:
            try:
                best_move, is_search_complete = self._queue.get(block=False)
                print("dequeue", best_move)
            except Empty:
                best_move, is_search_complete = None, False

            if time() - self._time >= AGENT_MAX_SEARCH_SECS + AGENT_SEC_THRESHOLD:
                print("send interrupt")
                self._agent.interrupt()
                is_search_complete = True

            self._move = best_move or self._move
            self._done = is_search_complete
            if is_search_complete:
                print("agent queues", self._move)

        if best_move and is_search_complete:
            self._move = None
            return best_move
