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
    def __init__(self, name, note_pool, prob_matrix="default", tempo_mult=1, steps_between_recalc="default"):
        self.name = name
        self.note_pool = note_pool # Maybe rename to "base_sequence"...
        self.tempo_mult = tempo_mult

        if prob_matrix == "default":
            self.prob_matrix = []
            for count in range(len(self.note_pool)):
                prob_list = []
                for i in range(len(self.note_pool)):
                    if i == count:
                        prob_list.append(1)
                    else:
                        prob_list.append(0)
                self.prob_matrix.append(prob_list)
        else:
            self.prob_matrix = prob_matrix # This argument should be a list of any length, whose elements are a list of probability weights of len(base_sequence) that add up to 1
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

        note_on_msg = 0x90 + self.channel - 1 # Subtract 1, because logical MIDI channel 1 is actually 0
        note_off_msg = 0x80 + self.channel - 1 # Subtract 1, because logical MIDI channel 1 is actually 0

        if isinstance(self.sequencer.out, numbers.Number):
            if self.follow_mode == True:
                self.current_note = int(degree_to_mode(self.sequencer.out, self.octave)) # should be MIDI value
            else:
                self.current_note = self.sequencer.out
        else:
            self.current_note = "x"

        if isinstance(self.sequencer.last_out, numbers.Number):
            if self.follow_mode == True:
                self.last_note = int(degree_to_mode(self.sequencer.last_out, self.octave)) # should be MIDI value
            else:
                self.last_note = self.sequencer.last_out
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
                    midiout.send_message([note_off_msg, self.last_note, 0]) # note off message for last note played
            else:
                if self.last_note != 'x':
                    midiout.send_message([note_off_msg, self.last_note, 0]) # note off message for last note played
                    midiout.send_message([note_on_msg, self.current_note, 110]) # note on message for last note played
                else:
                    midiout.send_message([note_on_msg, self.current_note, 110]) # note on message for last note played


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

def degree_to_mode(degree, octave=0, key=global_key, mode=global_mode):
    # Make it so degrees that are out of mode's range result in higher or lower notes (e.g. if degree 0 translates to MIDI 60, degree of -1 might be MIDI 59, or 58, depending on the mode)
    return global_key + (octave * 12) + global_mode[degree % len(global_mode)]

def update(generator_list):
    for i in range(len(generator_list)):
        generator_list[i].update()

# INITIALIZE SEQUENCERS

sequencer_list = [] # inistalizes list where all attractors are stored

sequencer_list.append(Sequencer("synth0", [0,1,2,3,"x",3,2,1]))
sequencer_list.append(Sequencer("synth1", [1, 2, 3, 4]))
# [[1, 0, 0],[0.1, 0.4, 0.5], [0, 0.7, 0.3]]
sequencer_list.append(Sequencer("synth2", [0, 1, 2, 3, 'x'], [[1, 0, 0, 0, 0], [0,0.8,0,0,0.2],[0.1, 0.2, 0.2, 0, 0.5], [0, 0.7, 0.3, 0, 0]], 2))

sequencer_list.append(Sequencer("drum0", [36, "x"], [[1,0],[0.5,0.5],[0, 1],[0.6,0.4]], 4)) # Would be nice to enter a string and have it convert to a list.

#INITIALIZE PLAYERS

player_list = []

player_list.append(Player(sequencer_list[0], "player0", True, -1))
player_list.append(Player(sequencer_list[1],"player1", True, 0))
player_list.append(Player(sequencer_list[2], "player2", True, 1))
player_list.append(Player(sequencer_list[3], "drum0_player", False, 0, 2))


# START PLAYING THE ACTUAL COMPOSITION

while t < 1000 / seconds_per_cycle:

    if t % (4 * cycles_per_beat) == 0: # Add this functionality within Attractor/Sequencer.update itself as well
        for i in range(len(sequencer_list)):
            sequencer_list[i].recalc()
            sequencer_list[i].tempo_mult = numpy.random.choice([1,2,3,4], 1, True, [0.25,0.25,0.25,0.25])[0]
            #attractor_list[i].pos = 0


    update(sequencer_list)

    # Need a way to filter inputs of wrong type (in .update()) for each variable that will be modified externally in each class

    # global_key = 60 + int(sequencer_list[1].out)

    if global_key_temp != global_key and global_key_temp != "init":
        for i in range(len(player_list)):
            midiout.send_message([0x80, int(player_list[i].last_note), 0]) # send off message to last note played
            midiout.send_message([0x80, int(player_list[i].current_note), 0]) # send off message to current note playing

    global_key_temp = global_key

    update(player_list)


    t = t + 1
    time.sleep(seconds_per_cycle - (time.time() % seconds_per_cycle))
