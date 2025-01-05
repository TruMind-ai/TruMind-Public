#!/usr/bin/python3

import os
import re
import sys
import click
from pathlib import Path
import submit_util as SUBUTIL


# This script is a demo of the submitter logic that submits using the demo data in this repo
# Clients can run this script to confirm the configuration is working,
# but for real usage they should write their own code that calls methods on the BatchSubmitter object


# Configure a BatchSubmitter with some dummy data
def build_submitter(clientcode):

    submitter = SUBUTIL.BatchSubmitter(clientcode)

    vttdata = {
        1 : "FinanceProCoaching_Anon.vtt",
        2 : "BigTechCoaching_Anon.vtt"
    }

    datadir = Path(__file__).parent.parent.parent / "data" / "real"

    for transid, vttfile in vttdata.items():
        fullpath = datadir  / vttfile
        submitter.add_vtt_file(str(fullpath), transid)

    return submitter


@click.command()
@click.option('--checkconfig', default=True, help='Run the configuration checker')
def submit(checkconfig):
    clientcode = SUBUTIL.get_client_code()
    print(f"Testing submission utility with client code {clientcode}")

    # This is a generic configuration check
    if checkconfig:
        SUBUTIL.ConfirmConfig(clientcode).run_check()


    submitter = build_submitter(clientcode)
    submitter.submit()


if __name__ == '__main__':
    submit()

