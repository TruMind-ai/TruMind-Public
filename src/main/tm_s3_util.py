
import boto3
from datetime import datetime, timezone


TRUMIND_BUCKET = "trumind-main"


def get_utc_today_iso():
    fulliso = datetime.now(timezone.utc).isoformat()
    return fulliso[:10]
    

def seconds_past_midnight_utc():

    # Get the current UTC time
    utcnow = datetime.now(timezone.utc)
    utcmid = utcnow.replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate seconds since midnight
    return round((utcnow - utcmid).total_seconds())




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


# This is a generator, in theory a client could have more than 1000 objects
# For clients, this will only work if the prefix key matches their subfolder
def generate_folder_objects(prefixkey):

    ctoken = None
    s3_client = boto3.client('s3')

    while True:

        params = {'Bucket': TRUMIND_BUCKET, 'Prefix': prefixkey}

        if ctoken:
            params['ContinuationToken'] = ctoken

        response = s3_client.list_objects_v2(**params)

        yield from response.get('Contents', [])

        # Check if there are more objects to retrieve, if not, we're done
        if not response.get('IsTruncated'):
            break

        ctoken = response.get('NextContinuationToken')

