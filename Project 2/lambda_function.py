import boto3
from datetime import datetime, timezone, timedelta

# Configuration
BUCKET_NAME = 'imageprocessing-b11g13'  # Replace with your bucket name
DAYS_THRESHOLD = 30

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    deleted_files = []
    threshold_date = datetime.now(timezone.utc) - timedelta(days=DAYS_THRESHOLD)

    response = s3.list_objects_v2(Bucket=BUCKET_NAME)

    if 'Contents' in response:
        for obj in response['Contents']:
            if obj['LastModified'] < threshold_date:
                s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                deleted_files.append(obj['Key'])

    print(f"Deleted files older than {DAYS_THRESHOLD} days:")
    for file in deleted_files:
        print(f" - {file}")

    return {
        'statusCode': 200,
        'body': f"Deleted {len(deleted_files)} files."
    }