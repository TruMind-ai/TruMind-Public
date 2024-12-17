
import os
import sys
import time
import copy
import string
import shutil
from collections import deque


# This represents a full VTT file, which is composed of a small amount of header info,
# plus the list of VTT blocks
# It has a tool to generate a "collapsed" form, which strips out the timing info and the tuples,
# and combines consecutive speaker blocks into a single block.
# It also has a tool for basic anonymization of the transcript, which simply means 
# swapping out the speaker names for generic titles ("Speaker 1", etc)
class VttFile:

    def __init__(self):
        self.blocks = None


    def anonymize(self):

        def partname(idx):
            assert idx < 26, f"Too many speakers in this transcript!"
            return f"Speaker {string.ascii_uppercase[idx]}"

        speakermap =  { sp : partname(idx) for idx, sp in enumerate(self.get_speaker_set()) }
        return self.remap_speaker(speakermap)


    def remap_speaker(self, speakermap):
        newinfo = VttFile()
        newinfo.blocks = [block.change_speaker(speakermap) for block in self.blocks]
        return newinfo


    # This yields a list of lines that represent a collapsed form of the transcript,
    # which is more suitable for sending to LLMs.
    # This form ellides indexes and timestamps.
    # When the same speaker speaks multiple times in a row, it leaves out the header information
    # For subsequent utterances.
    def gen_collapsed_form(self):

        lastspeaker = None

        for block in self.blocks:
            if block.speaker != lastspeaker:
                yield ""
                yield ""
                yield f"{block.speaker}:"
                lastspeaker = block.speaker

            yield block.text.strip()


    def gen_file_lines(self):

        yield "WEBVTT"
        yield ""

        for block in self.blocks:
            yield from block.regenerate()



    def write_collapsed_form(self, filepath):

        with open(filepath, "w") as fh:
            for line in self.gen_collapsed_form():
                fh.write(line)
                fh.write("\n")


    def write_to_file(self, filepath):

        with open(filepath, 'w') as fh:
            for line in self.gen_file_lines():
                fh.write(line)
                fh.write("\n")


    def read_from_file(self, filepath):

        assert os.path.exists(filepath), f"File path {filepath} does not exist"

        vdeq = deque([line for line in open(filepath)])

        header = vdeq.popleft().strip()
        assert header == "WEBVTT", f"Expected to see a header line WEBVTT, but saw {header}"


        def genblocks():

            while vdeq:

                if len(vdeq[0].strip()) == 0:
                    vdeq.popleft()
                    continue

                yield VttFormatBlock().absorb(vdeq)


        self.blocks = list(genblocks())



        print(f"Read {len(self.blocks)} blocks from file path {filepath}")

        return self

    def get_speaker_set(self):
        spset = set([block.speaker for block in self.blocks])
        return spset


# This is a single block of VTT text corresponding to one speaker.
# It has an index, some timing information, the speaker name, and the text.
class VttFormatBlock:

    def __init__(self):

        self.index = None
        self.timetuple = None
        self.speaker = None
        self.text = None


    def absorb(self, infodeq):

        self.index = int(infodeq.popleft())
        self.timetuple = infodeq.popleft().strip()

        infoline = infodeq.popleft().strip().split(":")

        self.speaker = infoline[0]
        self.text = infoline[1]

        return self

    def change_speaker(self, speakermap):

        assert self.speaker in speakermap, f"Speaker {self.speaker} not found in speaker remap, {speakermap.keys()}"
        newblock = copy.copy(self)

        newblock.speaker = speakermap[self.speaker]
        return newblock


    def regenerate(self):
        yield f"{self.index}"
        yield f"{self.timetuple}"
        yield f"{self.speaker}: {self.text}"
        yield ""






