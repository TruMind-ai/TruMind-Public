
import boto3


TRUMIND_BUCKET = "trumind-main"

# TODO: possibly use a global session, and create clients from the session

def read_generic_s3(fullkey):

    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=TRUMIND_BUCKET, Key=fullkey)
    content = response['Body'].read()
    return content.decode('utf-8')


# Clients should never need to delete objects
# The data will be purged according to the retention policy
def delete_object(fullkey):
    boto3.client('s3').delete_object(Bucket=TRUMIND_BUCKET, Key=fullkey)


def s3_upload(iodata, fullkey):

    s3_client = boto3.client('s3')
    s3_client.put_object(Body=iodata, Bucket=TRUMIND_BUCKET, Key=fullkey)
