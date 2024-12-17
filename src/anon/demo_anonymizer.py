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

def anonymize(inputfile):

    assert os.path.exists(inputfile), f"Input file {inputfile} does not exist"
    assert inputfile.endswith(".vtt"), f"Expected a VTT file, found {inputfile}"




if __name__ == '__main__':


    


