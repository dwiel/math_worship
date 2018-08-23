import time
import rtmidi
import atexit
import numbers
"""
 IMPORTANT: INSTALL the correct library: pip install python-rtmidi
# there is another library rtmidi-python, which is NOT the one you want
# you want python-rtmidi!
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


class Player():
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
            self.current_note = int(degree_to_mode(sequencer.out, self.octave)) # should be MIDI value
        else:
            self.current_note = sequencer.out

        if isinstance(sequencer.last_out, numbers.Number):
            self.last_note = int(degree_to_mode(sequencer.last_out, self.octave)) # should be MIDI value
        else:
            self.last_note = sequencer.last_out

        if int(sequencer.pos) == int(sequencer.last_pos):
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
            self.current_note = sequencer.out

        if isinstance(sequencer.last_out, numbers.Number):
            self.last_note = int(36 + sequencer.last_out) # should be MIDI value
        else:
            self.last_note = sequencer.last_out

        if int(sequencer.pos) == int(sequencer.last_pos):
            self.play_me = False
        else:
            self.play_me  = True

        if self.play_me == True or self.init == True:

            self.init = False

            if self.current_note == 'x':
                if self.last_note != 'x':
                    midiout.send_message([0x81, self.last_note, 0]) # note off message for last note played
            else:
                if self.last_note != 'x':
                    midiout.send_message([0x81, self.last_note, 0]) # note off message for last note played
                    midiout.send_message([0x91, self.current_note, 110]) # note on message for last note played
                else:
                    midiout.send_message([0x91, self.current_note, 110]) # note on message for last note played


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
global_mode = [0, 2, 4, 7, 9] # "major pentatonic"
# ^ should information about key and mode be stored in a dict/tuple/...? Ask Zach!

def degree_to_mode(degree, octave=0, key=global_key, mode=global_mode):
    return global_key + (octave * 12) + global_mode[degree % len(global_mode)]

# INITIALIZE GENERATOR OBJECTS

sequencer_list = [] # initializing the list where all sequencers will be stored

sequencer_list.append(Sequencer("synth0", [0,1,2,3,"x",3,2,1], 1, 2))
sequencer_list.append(Sequencer("synth1", [0,1,"x",3], 1, 1))
sequencer_list.append(Sequencer("synth2", [0,2,0,1,2,3,"x",3,4,3,2,1], 1, 4))
sequencer_list.append(Sequencer("synth3", [0,2,0,1,2,3,"x",3,4,3,2,1], 1, 3))

sequencer_list.append(Sequencer("drum0", [0,"x",6,"x",0,"x",6,"x"], 1, 4)) # Would be nice to enter a string and have it convert to a list.
sequencer_list.append(Sequencer("invisible1", [0.5, 1, 2], 1, 0.125))
sequencer_list.append(Sequencer("invisible2", [0.5, 1, 2, 3], 1, 0.125))


player_list = [] #inistalizes list where all players are stored

player_list.append(Player("player0", 0))
player_list.append(Player("player1", -1))
player_list.append(Player("player2", 1))
player_list.append(Player("player3", 2))


drummer0 = Drummer("drum0_player")

# START PLAYING THE ACTUAL COMPOSITION

while t < 1000 / seconds_per_cycle:


    for i in range(len(sequencer_list)):
        sequencer_list[i].update()

        # This is where the mappings/connections between sequences are defined
        # We need a "map" function that maps inputs to ouputs iff they are numeric

        if isinstance(sequencer_list[1].out, numbers.Number):
            sequencer_list[0].increment = sequencer_list[1].out + 2

        #sequencer_list[1].tempo_mult = sequencer_list[4].out
        if isinstance(sequencer_list[0].out, numbers.Number):
            sequencer_list[1].increment = sequencer_list[0].out + 3

        #sequencer_list[2].tempo_mult = sequencer_list[4].out
        #sequencer_list[2].block_size = sequencer_list[1].out + 1
        #sequencer_list[2].block_start = sequencer_list[1].out - 1
        if isinstance(sequencer_list[0].out, numbers.Number):
            sequencer_list[2].increment = sequencer_list[0].out + 4

        if isinstance(sequencer_list[0].out, numbers.Number):
            sequencer_list[3].increment = sequencer_list[0].out + sequencer_list[5].out

        sequencer_list[3].tempo_mult = sequencer_list[5].out + sequencer_list[6].out

    #global_key = 60 + int(sequencer_list[1].out)

    if global_key_temp != global_key and global_key_temp != "init":
        for i in range(len(player_list)):
            midiout.send_message([0x80, int(player_list[i].last_note), 0]) # send off message to last note played
            midiout.send_message([0x80, int(player_list[i].current_note), 0]) # send off message to current note playing

    global_key_temp = global_key

    for i in range(len(player_list)):
        player_list[i].play(sequencer_list[i])



    drummer0.play(sequencer_list[4])


    t = t + 1
    time.sleep(seconds_per_cycle - (time.time() % seconds_per_cycle))
