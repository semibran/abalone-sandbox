from math import inf

class Anim:
    blocking = False
    duration = inf
    delay = 0
    loop = False

    def __init__(self, duration=0, delay=0, loop=False, target=None, on_start=None, on_end=None):
        self.duration = duration or self.duration
        self.delay = delay or self.delay
        self.time = -self.delay
        if loop: self.loop = loop
        self.target = target
        self.on_start = on_start
        self.on_end = on_end
        self.done = False

    def end(self):
        self.done = True
        self.on_end and self.on_end()

    def update(self):
        if self.done:
            return -1

        if self.time == 0:
            self.on_start and self.on_start()

        self.time += 1
        if self.duration and self.time == self.duration and not self.loop:
            self.end()

        if self.time < 0:
            return 0

        return self.time
