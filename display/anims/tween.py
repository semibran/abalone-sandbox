from display.anims import Anim

class TweenAnim(Anim):
    blocking = True

    def __init__(self, easing=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._easing = easing
        self._pos = 0

    @property
    def pos(self):
        return self._pos

    def update(self):
        time = super().update()

        if self.done:
            self._pos = 1
            return 1

        self._pos = max(0, time / self.duration)
        if self._easing:
            self._pos = self._easing(self._pos)

        return self._pos
