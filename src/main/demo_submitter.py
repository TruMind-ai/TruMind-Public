#!/usr/bin/python3

import os
import re
import sys
import click

from submit_util import ConfirmConfig


@click.command()
def submit():
    print("Testing submission utility")
    cconfig = ConfirmConfig('dburfoot')
    cconfig.run_check()

if __name__ == '__main__':
    submit()


