''' Module | blok_upload '''

import config
from boto3 import session
from boto3.s3.transfer import S3Transfer
from botocore.config import Config

import settings  # pylint: disable=E0401

# ---------------------------------------------------------------------------- #
#                                 Storage Setup                                #
# ---------------------------------------------------------------------------- #
bucket_session = session.Session()

boto_config = Config(
    retries={
        'max_attempts': 3,
        'mode': 'standard'
    }
)
config.boto_client = bucket_session.client(
    's3', region_name=settings.REGION_NAME,
    endpoint_url=settings.ENDPOINT_URL,
    aws_access_key_id=settings.ACCESS_ID,
    aws_secret_access_key=settings.SECRET_KEY,
    config=boto_config
)
config.boto_transfer = S3Transfer(config.boto_client)


# ---------------------------------------------------------------------------- #
#                               Upload Functions                               #
# ---------------------------------------------------------------------------- #

# -------------------------------- File Upload ------------------------------- #
def bucket_upload(source_directory, destination_directory, file_name, bucket_name):
    '''
    Uploads images to cloud bucket storage.
    '''
    transfer = config.boto_transfer

    transfer.upload_file(
        f'{source_directory}/{file_name}.png',
        f'{bucket_name}', f'{destination_directory}/{file_name}.png'
    )


# ------------------------------- Stream Upload ------------------------------ #
def stream_upload(bucket, key, body, content_type, permissions=None):
    '''
    Uploads images to cloud bucket storage.
    '''
    config.boto_client.put_object(
        Bucket=str(bucket),
        Key=str(key),
        Body=body,
        ContentType=str(content_type)
    )

    if permissions is not None:
        config.boto_client.put_object_acl(
            ACL=str(permissions),
            Bucket=str(bucket),
            Key=str(key)
        )
