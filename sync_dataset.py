"""
Project 01: Sync Local Dataset to S3 with Versioning
Syncs a local directory to S3, tracks versions, and provides a summary.
"""

import boto3
import os
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "my-ml-datalake-01")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
S3_PREFIX = "datasets/"


def compute_md5(file_path):
    """Compute MD5 hash of a file for change detection."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_s3_etag(s3_client, bucket, key):
    """Get the ETag (MD5) of an existing S3 object, or None if not found."""
    try:
        response = s3_client.head_object(Bucket=bucket, Key=key)
        return response["ETag"].strip('"')
    except s3_client.exceptions.ClientError:
        return None


def sync_directory(local_dir, bucket_name, s3_prefix):
    """Sync a local directory to S3, uploading only changed files."""
    s3_client = boto3.client("s3", region_name=REGION)
    local_path = Path(local_dir)

    if not local_path.exists():
        print(f"ERROR: Directory '{local_dir}' does not exist.")
        return

    files = [f for f in local_path.rglob("*") if f.is_file()]
    if not files:
        print(f"No files found in '{local_dir}'.")
        return

    stats = {"uploaded": 0, "skipped": 0, "failed": 0}

    print(f"\nSyncing '{local_dir}' -> s3://{bucket_name}/{s3_prefix}")
    print(f"Found {len(files)} file(s)\n")

    for file_path in sorted(files):
        relative = file_path.relative_to(local_path)
        s3_key = f"{s3_prefix}{relative}"
        local_md5 = compute_md5(file_path)
        remote_etag = get_s3_etag(s3_client, bucket_name, s3_key)

        if local_md5 == remote_etag:
            print(f"  SKIP  {relative} (unchanged)")
            stats["skipped"] += 1
            continue

        try:
            s3_client.upload_file(
                str(file_path),
                bucket_name,
                s3_key,
                ExtraArgs={
                    "Metadata": {
                        "local-md5": local_md5,
                        "sync-time": datetime.now(timezone.utc).isoformat(),
                        "source-path": str(relative),
                    }
                },
            )
            action = "UPDATE" if remote_etag else "UPLOAD"
            print(f"  {action} {relative}")
            stats["uploaded"] += 1
        except Exception as e:
            print(f"  FAIL  {relative}: {e}")
            stats["failed"] += 1

    print(f"\nSync complete: {stats['uploaded']} uploaded, "
          f"{stats['skipped']} skipped, {stats['failed']} failed")
    return stats


def list_versions(bucket_name, s3_prefix):
    """List object versions in the bucket to demonstrate versioning."""
    s3_client = boto3.client("s3", region_name=REGION)

    print(f"\nObject versions in s3://{bucket_name}/{s3_prefix}")
    print("-" * 70)

    response = s3_client.list_object_versions(Bucket=bucket_name, Prefix=s3_prefix)

    versions = response.get("Versions", [])
    if not versions:
        print("  No versions found.")
        return

    for v in versions:
        latest = " (latest)" if v["IsLatest"] else ""
        print(f"  {v['Key']}")
        print(f"    Version: {v['VersionId']}{latest}")
        print(f"    Size:    {v['Size']} bytes")
        print(f"    Date:    {v['LastModified']}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync local dataset to S3")
    parser.add_argument("local_dir", help="Local directory to sync")
    parser.add_argument("--prefix", default=S3_PREFIX, help="S3 key prefix (default: datasets/)")
    parser.add_argument("--list-versions", action="store_true", help="List object versions after sync")
    args = parser.parse_args()

    sync_directory(args.local_dir, BUCKET_NAME, args.prefix)

    if args.list_versions:
        list_versions(BUCKET_NAME, args.prefix)
