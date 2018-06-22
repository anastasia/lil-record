import os
import boto3
from settings import S3_KEY, S3_SECRET, S3_LOCATION, S3_BUCKET

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET)


def upload(filepath, filename, folder="", bucket_name=S3_BUCKET):
    """
    Upload to s3. Allows programmatic creation of subfolders in bucket
    """
    uploaded_filepath = os.path.join(folder, filename)
    try:
        s3.upload_file(
            filepath,
            bucket_name,
            uploaded_filepath)

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(S3_LOCATION, uploaded_filepath)
