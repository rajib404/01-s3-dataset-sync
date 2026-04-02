# Project 01: S3 Dataset Sync with Versioning

Sync a local ML dataset to AWS S3 with versioning enabled — track every change to your training data.

## What You'll Learn
- Creating S3 buckets programmatically with boto3
- Enabling and using S3 versioning
- Syncing local files to S3 with change detection (MD5 comparison)
- Attaching metadata to S3 objects

## Prerequisites
- AWS account with access keys configured
- Python 3.10+

## Setup

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
cp .env.example .env
# Edit .env with your AWS credentials
```

## Usage

### Step 1: Set up the S3 bucket
```bash
python setup_bucket.py
```

### Step 2: Generate sample data
```bash
python create_sample_data.py
```

### Step 3: Sync to S3
```bash
python sync_dataset.py sample_dataset/
```

### Step 4: Modify data and sync again to see versioning
```bash
# Regenerate data (creates different random values)
python create_sample_data.py

# Sync again — only changed files are uploaded
python sync_dataset.py sample_dataset/ --list-versions
```

## How It Works
1. **setup_bucket.py** — Creates the S3 bucket and enables versioning
2. **create_sample_data.py** — Generates sample CSV/JSON dataset
3. **sync_dataset.py** — Compares local MD5 hashes with S3 ETags, uploads only changed files, and can list all object versions

## Key Concepts
- **S3 Versioning**: Every overwrite creates a new version instead of replacing the object. Critical for ML data lineage.
- **ETag Comparison**: S3 returns MD5 hash as ETag for single-part uploads, enabling efficient change detection.
- **Object Metadata**: Custom metadata attached to each upload for tracking sync time and source path.
