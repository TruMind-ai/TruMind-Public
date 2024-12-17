#!/usr/bin/python3

import os
import re
import sys
import click
from pathlib import Path
from vtt_util import VttFile


@click.command()
@click.option('--inputfile', help='Path to the input VTT file')
@click.option('--outputfile', default=None, help='Path to the output VTT file, if not provided use add _anon')

def anonymize(inputfile, outputfile):
    assert os.path.exists(inputfile), f"Input file {inputfile} does not exist"
    assert inputfile.endswith(".vtt"), f"Expected a VTT file, found {inputfile}"

    vfile = VttFile().read_from_file(inputfile).anonymize()



    if outputfile == None:
        for line in vfile.gen_file_lines():
            print(line)

    else:
        vfile.write_to_file(outputfile)


if __name__ == '__main__':


    anonymize()


