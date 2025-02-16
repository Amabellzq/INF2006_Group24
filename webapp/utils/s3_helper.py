import boto3

from werkzeug.utils import secure_filename
from botocore.exceptions import NoCredentialsError, ClientError
from webapp.config import Config  # ✅ Ensure correct import path

<<<<<<< HEAD
# ✅ Create S3 client using IAM Role authentication
try:
    s3 = boto3.client(
        "s3",
        region_name=Config.AWS_S3_REGION,
        endpoint_url=Config.AWS_S3_VPC_ENDPOINT  # ✅ Force S3 Gateway Endpoint
    )
except NoCredentialsError:
    print("❌ AWS IAM Role not detected. Ensure EC2 has an IAM Role attached.")

def upload_file_to_s3(file, folder="uploads/"):
    """Upload file to AWS S3 via the configured VPC Gateway Endpoint."""
=======
from webapp import Config

# ✅ Use IAM Role authentication (No AWS keys required)
s3 = boto3.client("s3", region_name=Config.AWS_S3_REGION)

def upload_file_to_s3(file, folder="uploads/"):
    """Upload file to AWS S3 via VPC Gateway Endpoint."""
>>>>>>> origin/jw
    try:
        filename = secure_filename(file.filename)
        s3_path = f"{folder}/{filename}"

<<<<<<< HEAD
        # ✅ Add Content-Type header to prevent S3 rejections
        extra_args = {
            "ContentType": file.content_type,
            "ACL": "private"  # Change to 'public-read' if needed
        }

        # ✅ Upload file using IAM Role authentication via VPC Gateway Endpoint
=======
        # ✅ Upload file using IAM Role authentication
>>>>>>> origin/jw
        s3.upload_fileobj(
            file,
            Config.AWS_S3_BUCKET,
            s3_path,
            ExtraArgs=extra_args
        )

<<<<<<< HEAD
        # ✅ Construct the S3 object URL using the VPC Gateway
        file_url = f"{Config.AWS_S3_VPC_ENDPOINT}/{Config.AWS_S3_BUCKET}/{s3_path}"
        return file_url

    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"❌ S3 Upload Error: {error_code} - {str(e)}")
        return None
    except NoCredentialsError:
        print("❌ AWS IAM Role not found. Ensure EC2 has IAM Role attached.")
        return None
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
=======
        # ✅ Construct S3 URL using VPC Endpoint
        file_url = f"{Config.AWS_S3_VPC_ENDPOINT}/{Config.AWS_S3_BUCKET}/{s3_path}"
        return file_url

    except Exception as e:
        print(f"❌ Error uploading to S3: {e}")
>>>>>>> origin/jw
        return None
