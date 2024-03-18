import unittest
import os
import boto3
import depcleaner
import random
import string
import time
import logging

logger = logging.getLogger(__name__)

level = logging.INFO
class TestDepcleaner(unittest.TestCase):

    if 'ENDPOINT_URL' in os.environ:
        endpoint_url = os.environ['ENDPOINT_URL']
        client = boto3.client('s3', endpoint_url=endpoint_url)
    else:
        client = boto3.client('s3')

    bucket = 'will-test123'
        # Fixed prefix
    prefix = "deploy"
    test_deployment_count = 12
    deployments_to_keep = 5

    @classmethod
    def setUpClass(cls):
        print("Setting up test environment with {} mock deployments...".format(TestDepcleaner.test_deployment_count))

        deployment_names = []

        
        # Calculate the maximum number of random characters to add (20 - length of prefix)
        max_random_chars = 20 - len(TestDepcleaner.prefix)
        
        # Generate N random strings
        for _ in range(TestDepcleaner.test_deployment_count):
            # Generate a random string of up to max_random_chars
            random_string_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=max_random_chars))
            
            # Combine the prefix and the random string to form the final string
            random_string = TestDepcleaner.prefix + random_string_suffix
            
            # Add the random string to the list
            deployment_names.append(random_string)

        for deployment in deployment_names:
            print("Populating mock deployment:{}".format(deployment))
            for root, dirs, files in os.walk('./deployment'):

                for filename in files:

                    # construct the full local path
                    local_path = os.path.join(root, filename)

                    # construct the full Dropbox path
                    relative_path = os.path.relpath(local_path, 'deployment')
                    s3_path = os.path.join(deployment, relative_path)

                    try:
                        TestDepcleaner.client.head_object(Bucket=TestDepcleaner.bucket, Key=s3_path)
                    except:
                        TestDepcleaner.client.upload_file(local_path, TestDepcleaner.bucket, s3_path)
            # A random time delay is introduced between copying each mock deployment.
            # This results in discrete intervals between deployments as similar to a 
            # real world scenario.
            random_sleep_time = random.randint(1, 5)
            time.sleep(random_sleep_time)

    @classmethod
    def tearDownClass(cls):

        paginator = TestDepcleaner.client.get_paginator("list_objects_v2")
        keys_to_delete = []
        for page in paginator.paginate(Bucket=TestDepcleaner.bucket, Prefix=TestDepcleaner.prefix):
            for object in page['Contents']:
                keys_to_delete.append(object['Key'])
            #keys.extend(page['Contents'])

        for key in keys_to_delete:
            response = TestDepcleaner.client.delete_object(
            Bucket=TestDepcleaner.bucket,
            Key=key
            )

    def test_check_deployment_count(self):
        # This test ensures the setupClass resulted in the correct amount of deployments
        # Its critical we verify this as we depend on this for the subsequent tests to 
        # be accurate. 
        deployments = depcleaner.get_deployments(TestDepcleaner.bucket)
        self.assertEqual(len(deployments), TestDepcleaner.test_deployment_count, 'The sum is wrong.')
        


    def test_clean_deployments(self):
    
        
        depcleaner.clean_deployments(TestDepcleaner.bucket, TestDepcleaner.deployments_to_keep)

        paginator = TestDepcleaner.client.get_paginator("list_objects_v2")

        # There's no such thing as a directory in S3, only objects and their key, and prefixes.  
        # As such to make this script managable in a high cardinality environment, 
        # we want to leverage the S3 API to get a listing of all of the common prefixes. 
        # This maps to what we logically think of as the deployment's directory.
        deployments = []
        for page in paginator.paginate(Bucket=TestDepcleaner.bucket,  Delimiter='/'):
            deployments.extend(page['CommonPrefixes'])



        self.assertEqual(len(deployments), TestDepcleaner.deployments_to_keep, 'The sum is wrong.')


if __name__ == '__main__':
    unittest.main()