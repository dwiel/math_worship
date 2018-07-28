import time
print("")


class Sequencer():
    def __init__(self, name, base_sequence, increment=1, tempo_mult=1, block_size=None, block_start=0):
        self.base_sequence = base_sequence
        self.name = name
        self.pos = 0
        self.increment = increment
        self.tempo_mult = tempo_mult

        if block_size is None:
            self.block_size = len(base_sequence)
        else:
            self.block_size = block_size

        self.block_start = block_start
        self.out = self.block()[0]
        self.last_out = "init"
        self.last_time = 0

    def block(self):
        return self.base_sequence[self.block_start:(self.block_start + self.block_size)]

    def update(self):

        block = self.block()

        cycles_per_step = float(cycles_per_beat) / self.tempo_mult
        self.pos += self.increment / cycles_per_step
        self.pos = self.pos % len(block)

        self.out = block[int(self.pos)]

        if self.last_out != self.out:
            print(self.name, self.out)
            # print 1000 * (0.5 - (time.time() - self.last_time))
            # self.last_time = time.time()
        self.last_out = self.out

        return self.out


seconds_per_cycle = .001

bpm = 120.0
cycles_per_beat = 1 / (bpm / 60 * seconds_per_cycle)
t = 0

fund_freq = 100

note_bank = [1, 1.25, 1.3, 1.5, 2]

seq1 = Sequencer("seq1", [1,2,3,4,5], 1, 1)
seq2 = Sequencer("seq2", [1,2,3], 1, 1)

while t < 5 / seconds_per_cycle:

    # seq2.tempo_mult = seq1.out
    # seq1.increment = seq2.out

    seq1.update()
    seq2.update()

    t = t + 1
    time.sleep(seconds_per_cycle - (time.time() % seconds_per_cycle))
