from time import time_ns


class MeanProfiler:

    def __init__(self):
        self._markers = {}
        self._time_start = None
        self._time_aggregate = 0
        self._num_calls = 0

    def start(self):
        self._markers[self._num_calls] = time_ns()
        return self._num_calls

    def stop(self, tag=None, label=""):
        if tag is None:
            tag = self._num_calls

        if tag not in self._markers:
            raise KeyError(f"tag {tag} was not registered")

        time_start = self._markers[tag]
        del self._markers[tag]

        self._time_aggregate += time_ns() - time_start
        self._num_calls += 1
        time_average = self._time_aggregate / self._num_calls / 1000

        if label:
            label += ": "
        print(f"{label}{time_average:.2f}µs/{self._num_calls}")
