
import random
import tm_s3_util as TMS3


def get_client_s3_folder(clientcode):
    return f"client/{clientcode}"


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


class SubmitUtil:

    def __init__(self):
        pass




