import boto3
from PIL import Image
import io

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Get bucket name and object key from event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Download the image from S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_data = response['Body'].read()

    # Open image using Pillow
    image = Image.open(io.BytesIO(image_data))

    # Compress the image
    compressed_image = io.BytesIO()
    image.save(compressed_image, format="JPEG", quality=50)  # Adjust quality as needed

    # Upload compressed image back to S3
    compressed_key = f"compressed/{object_key}"
    s3.put_object(Bucket=bucket_name, Key=compressed_key, Body=compressed_image.getvalue(), ContentType="image/jpeg")

    return {
        'statusCode': 200,
        'body': f"Image compressed and saved as {compressed_key}"
    }