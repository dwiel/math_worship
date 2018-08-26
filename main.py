import time
import rtmidi
import atexit
import numbers
import numpy
import random

"""
 IMPORTANT: INSTALL the correct library: pip install python-rtmidi
 there is another library rtmidi-python, which is NOT the one you want
 you want python-rtmidi!
"""

print("")

def exit_handler():
    # for each Player, send a midi note off message for previous and current note
    for i in range(len(player_list)):
        if isinstance(player_list[i].last_note, numbers.Number):
            midiout.send_message([0x80, player_list[i].last_note, 0])
        if isinstance(player_list[i].current_note, numbers.Number):
            midiout.send_message([0x80, player_list[i].current_note, 0])

atexit.register(exit_handler)

class Sequencer():
    def __init__(self, name, base_sequence, increment=1, tempo_mult=1, block_size=None, block_start=0):
        self.base_sequence = base_sequence
        self.name = name
        self.pos = 0
        self.last_pos = 0
        self.increment = increment
        self.tempo_mult = tempo_mult

        if block_size is None:
            self.block_size = len(base_sequence)
        else:
            self.block_size = block_size

        self.block_start = block_start
        #self.out = self.block()[0]
        self.out = base_sequence[0]
        self.last_out = "init"
        self.last_time = 0
        self.play_me = True
        print(base_sequence)



    def block(self):
        block_start = min(self.block_start % len(self.base_sequence), (self.block_size + self.block_start) % len(self.base_sequence))
        block_stop = max(block_start, ((self.block_size + self.block_start + 1) % len(self.base_sequence)))
        return self.base_sequence[block_start:block_stop]


    def update(self):

        self.last_out = self.out
        self.last_pos = self.pos

        #block = self.block()

        cycles_per_step = float(cycles_per_beat) / self.tempo_mult
        self.pos += (1 / cycles_per_step)
        #self.pos = self.pos % len(block)
        #self.out = block[int(self.pos)]
        self.pos = self.pos % len(self.base_sequence)
        self.out = self.base_sequence[int(self.pos)]

        if self.last_out != self.out:
            #self.pos = (self.pos + self.increment - 1) % len(block)
            #self.out = block[int(self.pos)]
            self.pos = (self.pos + self.increment - 1) % len(self.base_sequence)
            self.out = self.base_sequence[int(self.pos)]

            print(self.name, self.out)

        return self.out

class Attractor():
    def __init__(self, name, note_pool, prob_matrix, tempo_mult=1, steps_between_recalc="default"):
        self.name = name
        self.note_pool = note_pool
        self.tempo_mult = tempo_mult
        self.prob_matrix = prob_matrix # this argument should be a list of len(base_sequence), whose elements are a list of probability weights
        if steps_between_recalc == "default":
            self.steps_between_recalc = len(note_pool)
        else:
            self.steps_between_recalc = steps_between_recalc

        self.working_sequence = "init"
        self.pos = "init"
        self.last_pos = "init"
        self.out = 0
        self.last_out = 0

    def recalc(self):

        self.working_sequence = []

        for i in range(len(self.prob_matrix)):
            self.working_sequence.append(numpy.random.choice(self.note_pool, 1, True, self.prob_matrix[i])[0])

    def update(self):


        self.last_out = self.out
        self.last_pos = self.pos
        cycles_per_step = float(cycles_per_beat) / self.tempo_mult

        if self.pos == "init":
            self.pos = 0
            self.recalc()


        self.pos += (1 / cycles_per_step)
        self.pos = self.pos % len(self.working_sequence)

        if self.last_pos == "init":
            self.last_pos = 0
            self.out = self.working_sequence[int(self.pos)]
            print(self.name, self.out)

        elif int(self.pos) != int(self.last_pos):
            self.out = self.working_sequence[int(self.pos)]
            print(self.name, self.out)

        if isinstance(self.out, str) and self.out != "x":
            self.out = int(self.out)

        return self.out


class Player():
    def __init__(self, sequencer, name="a player", follow_mode=True, octave=0, channel=1):
        self.sequencer = sequencer
        self.name = name
        self.follow_mode = follow_mode
        self.octave = octave # This doesn't do anything yet.
        self.channel = channel # This doesn't do anyting yet.
        self.current_note = "init"
        self.last_note = "init"
        self.play_me = True
        self.init = True

    def update(self):

        #print(sequencer.pos)
        #print(sequencer.out)

        if isinstance(self.sequencer.out, numbers.Number):
            self.current_note = int(degree_to_mode(self.sequencer.out, self.octave)) # should be MIDI value
        else:
            self.current_note = "x"

        if isinstance(self.sequencer.last_out, numbers.Number):
            self.last_note = int(degree_to_mode(self.sequencer.last_out, self.octave)) # should be MIDI value
        else:
            self.last_note = "x"

        if int(self.sequencer.pos) == int(self.sequencer.last_pos):
            self.play_me = False
        else:
            self.play_me  = True

        if self.play_me == True or self.init == True:

            self.init = False

            if self.current_note == 'x':
                if self.last_note != 'x':
                    midiout.send_message([0x80, self.last_note, 0]) # note off message for last note played
            else:
                if self.last_note != 'x':
                    midiout.send_message([0x80, self.last_note, 0]) # note off message for last note played
                    midiout.send_message([0x90, self.current_note, 110]) # note on message for last note played
                else:
                    midiout.send_message([0x90, self.current_note, 110]) # note on message for last note played


            # TO DO: modify above code to divide amplitude by # of (non-muted/paused) Player objects

            print(self.name, self.current_note)
            return self.current_note

        else:

            return None


class Drummer():
    def __init__(self, name, octave=0, channel=1):
        self.name = name
        self.octave = octave # This doesn't do anything yet.
        self.channel = channel # This doesn't do anyting yet.
        self.current_note = "init"
        self.last_note = "init"
        self.play_me = True
        self.init = True

    def play(self, sequencer):

        #print(sequencer.pos)
        #print(sequencer.out)

        if isinstance(sequencer.out, numbers.Number):
            self.current_note = int(36 + sequencer.out) # should be MIDI value
        else:
            self.current_note = "x"

        if isinstance(sequencer.last_out, numbers.Number):
            self.last_note = int(36 + sequencer.last_out) # should be MIDI value
        else:
            self.last_note = "x"

        if int(sequencer.pos) == int(sequencer.last_pos):
            self.play_me = False
        else:
            self.play_me  = True

        if self.play_me == True or self.init == True:

            self.init = False

            if self.current_note == "x":
                if self.last_note != "x":
                    midiout.send_message([0x81, self.last_note, 0]) # note off message for last note played
            else:
                if self.last_note != "x":
                    midiout.send_message([0x81, self.last_note, 0]) # note off message for last note played
                    midiout.send_message([0x91, self.current_note, 110]) # note on message for current note
                else:
                    midiout.send_message([0x91, self.current_note, 110]) # note on message for current note


            # TO DO: modify above code to divide amplitude by # of (non-muted/paused) Player objects

            print(self.name, self.current_note)
            return self.current_note

        else:

            return None


midiout = rtmidi.MidiOut()
midiout.open_port(0)

time.sleep(5) # gives you time to connect midi outputs in patchage

seconds_per_cycle = .001

# GLOBAL VARIABLES FOR COMPOSITION

bpm = 120.0
cycles_per_beat = 1 / (bpm / 60 * seconds_per_cycle)
t = 0

# fund_freq = 100
global_key = 60 # "C" in MIDI
global_key_temp = "init"
global_mode = [0, 2, 4, 7, 11] # "major pentatonic"
# ^ should information about key and mode be stored in a dict/tuple/...? Ask Zach!

def degree_to_mode(degree, octave=0, key=global_key, mode=global_mode):
    # Make it so degrees that are out of mode's range result in higher or lower notes (e.g. if degree 0 translates to MIDI 60, degree of -1 might be MIDI 59, or 58, depending on the mode)
    return global_key + (octave * 12) + global_mode[degree % len(global_mode)]

def update(generator_list):
    for i in range(len(generator_list)):
        generator_list[i].update()

# INITIALIZE GENERATOR OBJECTS

attractor_list = [] # inistalizes list where all attractors are stored

attractor_list.append(Attractor("attractor0", [1, 2, 3], [[1, 0, 0],[0.1, 0.4, 0.5], [0, 0.7, 0.3]]))
attractor_list.append(Attractor("attractor1", [0, 1, 2, 3, 'x'], [[1, 0, 0, 0, 0], [0,0.8,0,0,0.2],[0.1, 0.2, 0.2, 0, 0.5], [0, 0.7, 0.3, 0, 0]], 2))
attractor_list.append(Attractor("drum0", [0, "x"], [[1,0],[0.5,0.5],[0, 1],[0.6,0.4]], 4)) # Would be nice to enter a string and have it convert to a list.

sequencer_list = [] # initializing the list where all sequencers will be stored

sequencer_list.append(Sequencer("synth0", [0,1,2,3,"x",3,2,1], 1, 1))
sequencer_list.append(Sequencer("synth1", [0,1, 2, 3, 4, 3, 2, 1], 1, 2))
sequencer_list.append(Sequencer("synth2", [0,2,0,1,2,3,"x",3,4,3,2,1], 1, 3))


sequencer_list.append(Sequencer("invisible1", [0.5, 1, 2], 1, 0.125))
sequencer_list.append(Sequencer("invisible2", [0.5, 1, 2, 3], 1, 0.125))


player_list = [] #inistalizes list where all players are stored

player_list.append(Player(sequencer_list[0], "player0", True, -1))
player_list.append(Player(attractor_list[0],"player1", True, 0))
player_list.append(Player(attractor_list[1], "player2", True, 1))

# Really, Drummer should be subsumed by Player; drum players just need "follow_mode = False" and octave = -2
drummer0 = Drummer("drum0_player")

# START PLAYING THE ACTUAL COMPOSITION

while t < 1000 / seconds_per_cycle:

    if t % (4 * cycles_per_beat) == 0: # Add this functionality within Attractor/Sequencer.update itself as well
        for i in range(len(attractor_list)):
            attractor_list[i].recalc()
            attractor_list[i].tempo_mult = numpy.random.choice([1,2,3,4], 1, True, [0.25,0.25,0.25,0.25])[0]
            #attractor_list[i].pos = 0


    update(sequencer_list)
    update(attractor_list)

    # We need a "map" function that maps inputs to ouputs iff they are numeric

    #global_key = 60 + int(sequencer_list[1].out)

    if global_key_temp != global_key and global_key_temp != "init":
        for i in range(len(player_list)):
            midiout.send_message([0x80, int(player_list[i].last_note), 0]) # send off message to last note played
            midiout.send_message([0x80, int(player_list[i].current_note), 0]) # send off message to current note playing

    global_key_temp = global_key

    update(player_list)



    drummer0.play(attractor_list[2])


    t = t + 1
    time.sleep(seconds_per_cycle - (time.time() % seconds_per_cycle))
