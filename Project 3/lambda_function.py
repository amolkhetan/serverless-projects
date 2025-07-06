import boto3
import json

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    unencrypted_buckets = []

    # List all buckets
    response = s3.list_buckets()
    buckets = response.get('Buckets', [])

    for bucket in buckets:
        bucket_name = bucket['Name']
        try:
            # Get the bucket's region
            location = s3.get_bucket_location(Bucket=bucket_name)
            region = location.get('LocationConstraint') or 'us-east-1'

            # Filter for us-west-2 only
            if region != 'us-west-2':
                continue

            # Try to get the bucket encryption configuration
            enc = s3.get_bucket_encryption(Bucket=bucket_name)
            rules = enc['ServerSideEncryptionConfiguration']['Rules']

        except s3.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ServerSideEncryptionConfigurationNotFoundError':
                # Bucket has no encryption
                unencrypted_buckets.append(bucket_name)
            elif error_code == 'AccessDenied':
                print(f"Access denied for bucket {bucket_name}")
            else:
                print(f"Error checking bucket {bucket_name}: {e}")

    if unencrypted_buckets:
        print("🚨 Unencrypted Buckets in us-west-2:")
        for name in unencrypted_buckets:
            print(f" - {name}")
    else:
        print("✅ All buckets in us-west-2 have server-side encryption enabled.")

    return {
        'statusCode': 200,
        'body': json.dumps({
            'unencrypted_buckets': unencrypted_buckets
        })
    }