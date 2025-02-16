import boto3
import os
from werkzeug.utils import secure_filename

# Load environment variables
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_REGION = os.getenv("AWS_S3_REGION")

# Create an S3 client (IAM Role-based authentication)
s3 = boto3.client("s3")


def upload_file_to_s3(file, folder="uploads/"):
    """Upload file to AWS S3 bucket and return its URL"""
    try:
        filename = secure_filename(file.filename)
        s3_path = f"{folder}{filename}"

        s3.upload_fileobj(
            file,
            AWS_S3_BUCKET,
            s3_path,
            ExtraArgs={"ACL": "public-read"}  # Set object to public-read
        )

        file_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{s3_path}"
        return file_url

    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
