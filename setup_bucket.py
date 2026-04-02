"""
Project 01: S3 Bucket Setup with Versioning
Creates an S3 bucket and enables versioning for ML data lake usage.
"""

import boto3
import os
import sys
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "my-ml-datalake-01")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def create_bucket(s3_client, bucket_name, region):
    """Create an S3 bucket if it doesn't already exist."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except s3_client.exceptions.ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            print(f"Creating bucket '{bucket_name}' in {region}...")
            if region == "us-east-1":
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region},
                )
            print(f"Bucket '{bucket_name}' created.")
        else:
            raise


def enable_versioning(s3_client, bucket_name):
    """Enable versioning on the bucket."""
    s3_client.put_bucket_versioning(
        Bucket=bucket_name,
        VersioningConfiguration={"Status": "Enabled"},
    )
    print(f"Versioning enabled on '{bucket_name}'.")


def verify_versioning(s3_client, bucket_name):
    """Verify versioning status."""
    response = s3_client.get_bucket_versioning(Bucket=bucket_name)
    status = response.get("Status", "Not set")
    print(f"Versioning status: {status}")
    return status == "Enabled"


def main():
    s3_client = boto3.client("s3", region_name=REGION)

    create_bucket(s3_client, BUCKET_NAME, REGION)
    enable_versioning(s3_client, BUCKET_NAME)

    if verify_versioning(s3_client, BUCKET_NAME):
        print("\nBucket is ready for ML data lake usage!")
    else:
        print("\nWARNING: Versioning could not be verified.")
        sys.exit(1)


if __name__ == "__main__":
    main()
