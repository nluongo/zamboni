#!/usr/bin/env python
"""
SageMaker entrypoint for the zamboni NHL prediction pipeline.

This script:
1. Fetches configuration from S3 (or uses local config if available)
2. Downloads required data files from S3
3. Runs the full NHL prediction pipeline
4. Uploads results back to S3

SageMaker-specific paths:
- Input data: /opt/ml/input/data/
- Output: /opt/ml/output/data/
- Model artifacts: /opt/ml/model/
"""

import argparse
import datetime
import logging
import os
import sys
import yaml
from pathlib import Path

# Add src to path so we can import zamboni modules
sys.path.insert(0, "/opt/program/src")

from zamboni.core import run

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def fetch_config_from_s3(bucket, key):
    """
    Fetch YAML configuration from S3.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key (path)
    
    Returns:
        dict: Parsed YAML configuration
    """
    import boto3
    
    s3_client = boto3.client("s3")
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        config = yaml.safe_load(response["Body"].read())
        logger.info(f"Loaded config from s3://{bucket}/{key}")
        return config
    except Exception as e:
        logger.error(f"Failed to fetch config from S3: {e}")
        raise


def load_config(config_file=None, s3_bucket=None, s3_config_key=None):
    """
    Load configuration from file or S3.
    
    Priority:
    1. S3 (if s3_bucket and s3_config_key provided)
    2. Local file (if config_file provided)
    3. Hardcoded defaults
    
    Args:
        config_file: Path to local YAML config
        s3_bucket: S3 bucket containing config
        s3_config_key: S3 key to config file
    
    Returns:
        dict: Configuration
    """
    config = None
    
    # Try S3 first if credentials available
    if s3_bucket and s3_config_key:
        try:
            config = fetch_config_from_s3(s3_bucket, s3_config_key)
            logger.info("Configuration loaded from S3")
            return config
        except Exception as e:
            logger.warning(f"Could not load config from S3: {e}")
    
    # Fall back to local file
    if config_file and os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_file}")
        return config
    
    # Default: require at least S3 bucket to be set
    raise ValueError(
        "No configuration found. Provide either --config-file or --s3-bucket/--s3-config-key"
    )


def ensure_directory(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description="SageMaker entrypoint for zamboni NHL prediction pipeline"
    )
    
    # Config source
    parser.add_argument(
        "--config-file",
        default=None,
        help="Path to local YAML configuration file"
    )
    parser.add_argument(
        "--s3-bucket",
        default=os.environ.get("CONFIG_S3_BUCKET"),
        help="S3 bucket containing configuration (or env: CONFIG_S3_BUCKET)"
    )
    parser.add_argument(
        "--s3-config-key",
        default=os.environ.get("CONFIG_S3_KEY", "config_sagemaker.yaml"),
        help="S3 key to config file (or env: CONFIG_S3_KEY, default: config_sagemaker.yaml)"
    )
    
    # Optional runtime overrides
    parser.add_argument(
        "--earliest-date",
        type=datetime.date.fromisoformat,
        default=None,
        help="Override earliest date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--latest-date",
        type=datetime.date.fromisoformat,
        default=None,
        help="Override latest date (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )
    
    # Pipeline control flags
    parser.add_argument(
        "--download",
        action="store_true",
        default=True,
        help="Download NHL data from API"
    )
    parser.add_argument(
        "--no-download",
        action="store_false",
        dest="download",
        help="Skip downloading NHL data"
    )
    parser.add_argument(
        "--train",
        action="store_true",
        default=True,
        help="Train predictors"
    )
    parser.add_argument(
        "--no-train",
        action="store_false",
        dest="train",
        help="Skip training"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    logger.info("Loading configuration...")
    config = load_config(
        config_file=args.config_file,
        s3_bucket=args.s3_bucket,
        s3_config_key=args.s3_config_key
    )
    
    # Extract data config
    data_config = config["data"]
    data_dir = data_config["dir"]
    
    # Ensure data directory exists
    ensure_directory(data_dir)
    
    # Extract pipeline config
    earliest_date = args.earliest_date or datetime.date.fromisoformat(config["earliest_date"])
    latest_date = args.latest_date or datetime.date.fromisoformat(config["latest_date"])
    predicters = config.get("predicters", [])
    
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Date range: {earliest_date} to {latest_date}")
    logger.info(f"Predictors: {[p['name'] for p in predicters]}")
    
    # Run the pipeline
    logger.info("Starting zamboni pipeline...")
    try:
        run(
            data_config=data_config,
            earliest_date=earliest_date,
            latest_date=latest_date,
            predicters=predicters,
            download=args.download,
            create_tables=True,
            force_recreate_tables=False,
            load_db=True,
            export=True,
            report=True,
            train=args.train,
            loglevel=args.loglevel,
        )
        logger.info("Pipeline completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
