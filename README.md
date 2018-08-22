# math_worship
Dependencies:

    apt-get install libjack-dev OR libjack-jackd2-dev
    apt-get install libasound2 libasound2-dev
    pip install python-rtmidi OR pip install --pre python-rtmidi

  Applications to plug into:
    JACK (qjackctl)
    patchage
    zynaddsubfx
    hydrogen
    jack-rack

  Other helpful applications:
    Kmidimon

Helpful links:
    https://en.wikipedia.org/wiki/Mode_(music) - Relevant music theory
    https://www.rapidtables.com/convert/number/binary-to-hex.html?x=10010100 - Binary to Hex converter
    https://arxiv.org/pdf/1705.05322.pdf - About MIDI messages
    https://www.nyu.edu/classes/bello/FMT_files/9_MIDI_code.pdf - More on MIDI messages
    http://trac.chrisarndt.de/code/wiki/python-rtmidi
    http://jackaudio.org/applications/ - JACK-compatible Applications

Software to facilitate development:
  Atom text editor
  black Python formatting tool https://pypi.org/project/black/18.3a0/#files
    pip install black==18.3a0
  entr http://www.entrproject.org/
