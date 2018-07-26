from pygame.time import Clock
import time

class Sequencer():
    def __init__(self, sequence, tempo_mult):
        self.sequence = sequence
        self.tempo_mult = tempo_mult
        self.last_out = 0

    def step(self):
        beat = int(t / (ticks_per_beat / self.tempo_mult))
        out = self.sequence[beat % len(self.sequence)]
        if self.last_out != out:
            print time.time()
        self.last_out = out
        return out


clock = Clock()
ticks_per_second = 10
bpm = 120.0
ticks_per_beat = ticks_per_second * 60 / bpm
t = 0

seq1 = Sequencer([1.5,0.33,3,2,0.5], 1)

while t < ticks_per_second * 5:
    # print seq1.step()
    seq1.step()
    clock.tick(ticks_per_second)
    t = t + 1
