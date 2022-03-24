from time import time
from core.agent import Agent
from threading import Thread
from queue import Queue, Empty
from config import AGENT_MAX_SEARCH_SECS, AGENT_SEC_THRESHOLD

class AgentOperator:

    def __init__(self):
        self._agent = Agent()
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

    def start_search(self, board, color):
        if self._thread:
            self._thread = None

        best_move_gen = self._agent.gen_best_move(
            board=board,
            player_unit=color
        )

        def worker():
            best_move = None
            done_search = False
            while not done_search:
                try:
                    best_move = next(best_move_gen)
                except StopIteration:
                    done_search = True

                done_search |= self._agent.interrupted
                if best_move or done_search:
                    print("yield", best_move, done_search)
                    self._queue.put((best_move, done_search))

        while self._queue.qsize():
            self._queue.get()
            self._queue.task_done()

        thread = Thread(target=worker)
        thread.daemon = True
        thread.start()

        self._thread = thread
        self._time = time()
        self._move = None
        self._done = False

        return thread

    def stop_search(self):
        self._agent.interrupt()
        self._move = None
        self._done = False

    def update(self):
        if self._done:
            best_move = self._move
            is_search_complete = self._done
        else:
            try:
                best_move, is_search_complete = self._queue.get_nowait()
                self._queue.task_done()
                print("dequeue", best_move)
            except Empty:
                best_move, is_search_complete = None, False

            if (not self._agent.interrupted
            and time() - self._time >= AGENT_MAX_SEARCH_SECS + AGENT_SEC_THRESHOLD):
                self._agent.interrupt()
                is_search_complete = True
                print("send interrupt")

            self._move = best_move or self._move
            self._done = is_search_complete
            if is_search_complete:
                print("agent queues", self._move)

        if best_move and is_search_complete:
            self._move = None
            return best_move
