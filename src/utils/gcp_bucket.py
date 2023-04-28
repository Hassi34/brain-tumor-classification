"""
Author : Hasanain Mehmood
Contact : hasanain@aicailber.com 
"""

from google.cloud import storage
import json
import pandas as pd

class BucketGCP:
    def __init__(self, bucket_name = None):
        self.client = storage.Client()
        self.project_id = self.client.project
        if bucket_name is None:
            try:
                self.bucket_name = self.project_id
            except Exception as e:
                print(
                    "Could not make the client session with default bucket name as the project name. Please provide the bucket name manually")
                raise e
        else:
            self.bucket_name = bucket_name
            
    def is_exists_bucket(self, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        return True if self.client.bucket(bucket_name).exists() else False
    
    def is_exists_blob(self, filename, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        if self.is_exists_bucket():
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(filename)
            return blob.exists()
        else:
            print(f'Specified bucket "{self.bucket_name}" does not exist, please create a bucket first')
    
    def create_bucket(self, storage_class: str="COLDLINE", location: str="US", bucket_name: str=None):
        """Creates a new bucket with the specified storage class and location

        Args:
            storage_class (str, optional): Storage class. Defaults to "COLDLINE".Available Selections = ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"]
            location (str, optional): Storage location. Defaults to "US".Available Selections = ["ASIA", "EU", "US"]
        """
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        if not self.is_exists_bucket(bucket_name):
            bucket = self.client.bucket(bucket_name)
            bucket.storage_class = storage_class
            new_bucket = self.client.create_bucket(bucket, location=location)
            print(f'Created bucket "{new_bucket.name}" in "{new_bucket.location}" with storage class "{new_bucket.storage_class}"')
        else:
            print(
                f'Bucket "{bucket_name}" already exists in project "{self.project_id}"')
            print('Skipping bucket creation...')
            
    def enable_versioning(self, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        if self.is_exists_bucket(bucket_name):
            bucket = self.client.get_bucket(bucket_name)
            bucket.versioning_enabled = True
            bucket.patch()
            print(f'Object versioning for Bucket "{bucket.name}" has been enabled')
        else:
            print(f'Specified bucket "{bucket_name}" does not exist, please create a bucket first')
       
    def disable_versioning(self, bucket_name: str=None):
        print(bucket_name)
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        if self.is_exists_bucket(bucket_name):
            bucket = self.client.get_bucket(bucket_name)
            bucket.versioning_enabled = False
            bucket.patch()
            print(f'Object versioning for Bucket "{bucket.name}" has been disabled')
        else:
            print(f'Specified bucket "{bucket_name}" does not exist, please create a bucket first')
            
    def list_blobs(self, bucket_name: str=None)-> list:
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        if self.is_exists_bucket(bucket_name):
            try:
                blobs = self.client.list_blobs(bucket_name)
                return [blob.name for blob in blobs]
            except Exception:
                print(f'There are not blobs available in "{bucket_name}"')
        else:
            print(f'Specified bucket "{bucket_name}" does not exist, please create a bucket first')
    
    def delete_blob(self, blob_name: str, alert: bool=True, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        if alert:
            usr_rsp = input(f'>>> "{blob_name}" will be permanently deleted from {bucket_name}. Type "Yes" if you want to delete else "No" :')
            if usr_rsp.title() == "Yes":
                bucket = self.client.bucket(bucket_name)
                blob = bucket.blob(blob_name)
                if blob.exists():
                    blob.delete()
                    print(f'Deleted blob "{blob_name}".')
                else:
                    print(f'Blob "{blob_name}" does not exists')
                
            elif usr_rsp.title() == "Yes":
                print('Did not Delete the blob.')
            else:
                print("!!!Invalid Response!!!")
        
        else:
            bucket = self.client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            if blob.exists():
                blob.delete()
                print(f'Deleted blob "{blob_name}".')
            else:
                print(f'Blob "{blob_name}" does not exists')
    
    def get_csv(self, filename:str, bucket_name: str=None)-> object:
        if bucket_name is None:
            bucket_name = self.bucket_name
        return pd.read_csv('gs://' + bucket_name + '/' +  filename, encoding='UTF-8')

    def get_excel(self, filename:str, bucket_name: str=None)-> object:
        if bucket_name is None:
            bucket_name = self.bucket_name
        return pd.read_csv('gs://' + bucket_name + '/' +  filename, encoding='UTF-8')

    def get_file_text(self, filename:str, bucket_name: str=None)-> str:
        if bucket_name is None:
            bucket_name = self.bucket_name
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(filename)
        if blob.exists():
            data = blob.download_as_string()
            return data
        else:
            print(f'"{filename}" does not exist')

    def get_json(self, filename:str, bucket_name: str=None)-> str:
        if bucket_name is None:
            bucket_name = self.bucket_name
        bucket = self.client.bucket(bucket_name)
        blob = bucket.blob(filename)
        if blob.exists():
            data = json.loads(blob.download_as_string())
            return data
        else:
            print(f'"{filename}" does not exist')

    def upload_file(self, source_file_name:str, destination_blob_name:str, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        try:
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(source_file_name)
            print(f'File "{source_file_name}" uploaded to "{destination_blob_name}".')
        except Exception as e:
            print(f'Could not upload "{source_file_name}" to "{destination_blob_name}".')
            raise e
        
    def download_file(self, source_blob_name:str, destination_file_name:str, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        try:
            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(source_blob_name)
            blob.download_to_filename(destination_file_name)
            print(f'File "{source_blob_name}" downloaded to "{destination_file_name}".')
        except Exception as e:
            print(f'Could not download "{source_blob_name}" to "{destination_file_name}".')
            raise e
            
    def empty_out_bucket(self, bucket_name: str=None):
        if bucket_name is None:
            bucket_name = self.bucket_name
        if self.is_exists_bucket(bucket_name):
            blobs = self.client.list_blobs(bucket_name)
            for blob in blobs:
                print(f'Deleting file {blob.name}...')
                blob.delete()  
        else:
            print(f'Bucket "{bucket_name}" Does Not exist')
    
    def dlt_bucket(self, bucket_name: str=None, alert: bool=True):
        if bucket_name is None:
            bucket_name = self.bucket_name
        
        if alert:
            usr_rsp = input(f'>>> Storage bucket "{bucket_name}" and all of its data will be permanently deleted. Type "Yes" if you want to delete else "No" :')
            if usr_rsp.title() == "Yes":
                self.empty_out_bucket(bucket_name)
                bucket = self.client.get_bucket(bucket_name)
                bucket.delete()
                print(f'Deleted "{bucket_name}".')
            elif usr_rsp.title() == "Yes":
                print('Did not delete the bucket')
            else:
                print("!!!Invalid Response!!!")
        else:
            self.empty_out_bucket(bucket_name)
            bucket = self.client.get_bucket(bucket_name)
            bucket.delete()
            print(f'Deleted "{bucket_name}".')
            
    def list_buckets(self):
        return [bucket for bucket in self.client.list_buckets()]
