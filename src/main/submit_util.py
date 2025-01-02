
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

    def run_check(self):

        self.write_probe_file()
        backresult = self.read_probe_file()

        # TODO: this needs to work
        # self.clean_up()
        # TODO: we also want to confirm client ability to List Objects

        assert backresult == self.probecontent
        print("Success, confirmed response is equal to original")

    def get_full_s3_key(self):
        clientfolder = get_client_s3_folder(self.client_code)
        filename = self.get_file_name()
        return f"{clientfolder}/{filename}"


    def get_file_name(self):
        return f"test_probe_{self.randx:08d}.txt"


    def read_probe_file(self):
        filename = self.get_full_s3_key()
        return TMS3.read_generic_s3(filename)


    def write_probe_file(self):
        TMS3.s3_upload(self.probecontent, self.get_full_s3_key())


    def clean_up(self):
        TMS3.delete_object(self.get_full_s3_key())


class SubmitUtil:

    def __init__(self):
        pass




