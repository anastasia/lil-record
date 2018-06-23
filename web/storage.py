import os
import boto3
from settings import S3_KEY, S3_SECRET, S3_LOCATION, S3_BUCKET

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET)


def upload(local_filepath, folder="", bucket_name=S3_BUCKET):
    """
    Upload to s3. Allows programmatic creation of subfolders in bucket
    """
    # import pdb; pdb.set_trace()
    filename = local_filepath.split('/')[-1]
    uploaded_filepath = os.path.join(folder, filename)
    try:
        s3.upload_file(
            local_filepath,
            bucket_name,
            uploaded_filepath)

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return "{}{}".format(S3_LOCATION, uploaded_filepath)


def get_contents(directory, bucket_name=S3_BUCKET):
    result = s3.list_objects(
        Bucket=bucket_name)
    contents = result.get('Contents')
    r = []
    for f in contents:
        d, fn = f.get('Key').split('/')
        if d == directory:
            r.append(f)
    return r


def download_archived(filename, type_of_file, bucket_name=S3_BUCKET):
    if type_of_file != "current":
        filepath = os.path.join("%ss" % type_of_file, filename)
    else:
        filepath = os.path.join("%ss" % type_of_file, filename)
    return download(filepath)


def download(s3_filepath, local_filename, bucket_name=S3_BUCKET):
    s3.download_file(
        bucket_name,
        s3_filepath,
        local_filename)
    return local_filename


def download_current_questions():
    dircontents = get_contents("current")
    questions = {}
    for file_obj in dircontents:
        name = file_obj['Key'].split('/')[-1]
        q = download(file_obj['Key'], name)
        with open(q, "r") as f:
            questions[file_obj['Key']] = f.read()

    return questions


def move_file(src, dest):
    print("moving file", src, dest)
    copy_source = {
        'Bucket': S3_BUCKET,
        'Key': src}
    print("copying questions")
    s3.copy(copy_source, S3_BUCKET, dest)
    print("delete question", src)
    s3.delete_object(Bucket=S3_BUCKET, Key=src)
    return dest



