import abc
import boto3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Storage(abc.ABC):
    pass

class S3Storage(Storage):
    """ Class for download/upload of files from S3 """

    def __init__(self, config):
        self.config = config
        self.bucket = config["s3_bucket"]
        self.db_source = config["db"]["s3_source"]
        self.db_local = config["db"]["local"]
        self.completed_source = config["completed_file"]["s3_source"]
        self.completed_local = config["completed_file"]["local"]
        self.today_source = config["today_file"]["s3_source"]
        self.today_local = config["today_file"]["local"]
        self.all_source = config["all_file"]["s3_source"]
        self.all_local = config["all_file"]["local"]

        if not self.completed_source or not self.completed_local:
            raise ValueError("Need both a source and local for completed file")
        if not self.today_source or not self.today_local:
            raise ValueError("Need both a source and local for today file")
        if not self.all_source or not self.all_local:
            raise ValueError("Need both a source and local for all file")

        self.s3 = boto3.client("s3")

    def get_file(self, bucket, source, local):
        try:
            self.s3.download_file(bucket, source, local)
        except Exception:
            logger.info(f"No file {source} found on S3, creating at {local}...")
            Path(local).touch()

    def upload_file(self, bucket, local, source):
        self.s3.upload_file(local, bucket, source)

    def get_files(self):
        self.get_file(self.bucket, self.db_source, self.db_local)
        self.get_file(self.bucket, self.completed_source, self.completed_local)
        self.get_file(self.bucket, self.today_source, self.today_local)
        self.get_file(self.bucket, self.all_source, self.all_local)

    def upload_files(self):
        self.upload_file(self.bucket, self.db_local, self.db_source)
        self.upload_file(self.bucket, self.completed_local, self.completed_source)
        self.upload_file(self.bucket, self.today_local, self.today_source)
        self.upload_file(self.bucket, self.all_local, self.all_source)
