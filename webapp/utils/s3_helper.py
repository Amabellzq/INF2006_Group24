import boto3
import os
from werkzeug.utils import secure_filename
from config import Config  # ✅ Import Config class

# ✅ Create S3 client (IAM Role automatically handles authentication)
s3 = boto3.client("s3", region_name=Config.AWS_S3_REGION)

def upload_file_to_s3(file, folder="uploads/"):
    """
    Upload file to AWS S3 bucket (accessed via VPC Gateway Endpoint).
    Returns the S3 file URL.
    """
    try:
        filename = secure_filename(file.filename)  # Ensure safe filename
        s3_path = f"{folder}{filename}"

        # ✅ Upload to S3 using IAM Role authentication
        s3.upload_fileobj(
            file,
            Config.AWS_S3_BUCKET,
            s3_path
        )

        # ✅ Construct the S3 URL using the VPC Endpoint DNS
        file_url = f"{Config.AWS_S3_VPC_ENDPOINT}/{Config.AWS_S3_BUCKET}/{s3_path}"
        return file_url

    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
