import time
import rtmidi
import atexit
# IMPORTANT: the correct library: pip install python-rtmidi
# there is another library rtmidi-python, which is NOT the one you want
# you want python-rtmidi!
print("")

def exit_handler():
    # for each Player, send a midi note off message for previous and current note
    for i in range(len(player_list)):
        midiout.send_message([0x80, player_list[i].last_note, 0])
        midiout.send_message([0x80, player_list[i].current_note, 0])

atexit.register(exit_handler)

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
        self.play_me = True

    def block(self):
        return self.base_sequence[self.block_start:(self.block_start + self.block_size)]

    def update(self):

        self.last_out = self.out
        block = self.block()

        cycles_per_step = float(cycles_per_beat) / self.tempo_mult
        self.pos += self.increment / cycles_per_step
        self.pos = self.pos % len(block)

        self.out = block[int(self.pos)]

        if self.last_out != self.out:
            print(self.name, self.out)
            # print 1000 * (0.5 - (time.time() - self.last_time))
            # self.last_time = time.time()
            self.play_me = True
        else:
            self.play_me = False

        return self.out

class Player():
    def __init__(self, name):
        self.name = name
        self.last_note = "init"
        self.current_note = "init"

    def play(self, sequencer):

        if sequencer.play_me == True:

            self.last_note = int(sequencer.last_out * fund_freq) # should be MIDI value
            self.current_note = int(sequencer.out * fund_freq) # should be MIDI value

            midiout.send_message([0x80, self.last_note, 0]) # note off message for last note played
            midiout.send_message([0x90, self.current_note, 110]) # note on, channel 1, frequency of note, velocity

            # TO DO: modify above code to divide amplitude by # of (non-muted/paused) Player objects

            print(self.name, self.current_note)
            return self.current_note

        else:

            return None


midiout = rtmidi.MidiOut()
midiout.open_port(0)
time.sleep(5) # gives you time to connect midi outputs in patchage

seconds_per_cycle = .001

bpm = 120.0
cycles_per_beat = 1 / (bpm / 60 * seconds_per_cycle)
t = 0

fund_freq = 40

note_bank = [1, 1.25, 1.3, 1.5, 2]

sequencer_list = []

sequencer_list.append(Sequencer("seq0", [1,1.25,1.5,1.75,2], 1, 1))
sequencer_list.append(Sequencer("seq1", [1,2,3], 1, 1))

player_list = []

player_list.append(Player("player1"))


while t < 120 / seconds_per_cycle:

    # seq2.tempo_mult = seq1.out
    # seq1.increment = seq2.out

    sequencer_list[0].tempo_mult = sequencer_list[1].out

    for i in range(len(sequencer_list)):
        sequencer_list[i].update()

    player_list[0].play(sequencer_list[0])

    t = t + 1
    time.sleep(seconds_per_cycle - (time.time() % seconds_per_cycle))
