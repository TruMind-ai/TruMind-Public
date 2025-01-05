
import os
import json
import base64
import random
import functools

from typing import Optional
from pydantic import BaseModel
import tm_s3_util as TMS3

CLIENT_CODE_ENV_VAR = "TRUMIND_CLIENT_CODE"


def get_client_s3_folder(clientcode):
    return f"client/{clientcode}"


# Lookup the client code from the environment variable
@functools.lru_cache(maxsize=1)
def get_client_code():
    ccode = os.environ.get(CLIENT_CODE_ENV_VAR, None)
    assert ccode != None, f"You must set the environment variable {CLIENT_CODE_ENV_VAR} with your client code"
    return ccode


def convert_file_b64(filepath=None, content=None):

    if filepath != None:
        with open(filepath, 'rb') as file:
            content = file.read()


    assert content != None, "You must submit either a file, or the file contents"

    # Encode the binary content to Base64
    return base64.b64encode(content).decode('utf-8')


class SubmitItem(BaseModel):
    transcript_id: int
    coach_id: Optional[str] = None
    client_id: Optional[str] = None
    vtt_data_b64: str




# Confirm that the currently configured user is able to write to the TruMind S3 bucket
# Write a dummy file, then read it again
class ConfirmConfig:

    def __init__(self, ccode):
        self.client_code = ccode
        self.randx = random.randint(0, 1000000)
        self.probecontent = f"Test Probe file access\n{self.randx}\n"

    # Main entry point: run all the checks: write, read, list, delete
    def run_check(self):

        self.write_probe_file()
        self.confirm_object_presence()
        backresult = self.read_probe_file()
        self.clean_up()

        assert backresult == self.probecontent
        print("Success, confirmed response is equal to original")

    def get_full_s3_key(self):
        clientfolder = get_client_s3_folder(self.client_code)
        filename = self.get_file_name()
        return f"{clientfolder}/{filename}"


    def get_file_name(self):
        return f"test_probe_{self.randx:08d}.txt"


    # This is really a check that the ListBucket permission has been granted properly
    def confirm_object_presence(self):
        searchkey = self.get_full_s3_key()
        clientfolder = get_client_s3_folder(self.client_code)
        for item in TMS3.generate_folder_objects(clientfolder):
            if item['Key'] == searchkey:
                print(f"Confirmed ListBucket and found file in subfolder")
                return

        assert False, f"Failed to find item with key {searchkey} in folder"


    def read_probe_file(self):
        filename = self.get_full_s3_key()
        return TMS3.read_generic_s3(filename)

    def write_probe_file(self):
        TMS3.s3_upload(self.probecontent, self.get_full_s3_key())

    def clean_up(self):
        probekey = self.get_full_s3_key()
        TMS3.delete_object(probekey)
        print(f"Probe key file {probekey} cleaned up successfully")


class BatchSubmitter:

    def __init__(self, ccode):
        self.record_list = []
        self.client_code = ccode

        self.today_iso = TMS3.get_utc_today_iso()
        self.submit_pair = self.__get_submit_pair()


    @staticmethod
    def __get_submit_pair():
        pastmid = TMS3.seconds_past_midnight_utc()
        return (pastmid, random.randint(0, 999999))


    def __get_s3_submit_key(self):
        pastmid, randsec = self.submit_pair
        folder = get_client_s3_folder(self.client_code)
        return f"{folder}/retain/{self.today_iso}/submit/batch__{pastmid:06}__{randsec:06}.json"


    # Add a record to the submission directly from VTT file content
    def add_vtt_data(self, vttdata, transcriptid, coachid=None, clientid=None):
        assert False, "TODO: implement this"

    # add a record to the submission from a VTT file
    # You must include at least a transcript ID
    # CoachID and client ID are optional
    def add_vtt_file(self, vttfile, transcriptid, coachid=None, clientid=None):

        assert vttfile.endswith(".vtt"), f"Expected a .vtt extension, found {vttfile}"
        assert os.path.exists(vttfile), f"Path {vttfile} does not exist"
        assert type(transcriptid) == int, f"The transcript ID must be an integer"

        vdata64 = convert_file_b64(filepath=vttfile)
        item = SubmitItem(transcript_id=transcriptid, vtt_data_b64=vdata64, coachid=coachid, clientid=clientid)

        self.record_list.append(item)


    def submit(self):
        jsondump = json.dumps({"records": [item.dict() for item in self.record_list]}, indent=2)

        fullkey = self.__get_s3_submit_key()
        TMS3.s3_upload(jsondump, fullkey)
        print(f"Submited {len(self.record_list)} records, total {len(jsondump)} characters of data to {fullkey}")



