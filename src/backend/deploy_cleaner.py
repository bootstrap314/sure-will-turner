import boto3
import logging
from datetime import datetime, timezone
import os

logger = logging.getLogger(__name__)

# This endpoint selector enables us to perform testing using localstack
if "ENDPOINT_URL" in os.environ:
    endpoint_url = os.environ["ENDPOINT_URL"]
    client = boto3.client("s3", endpoint_url=endpoint_url)
else:
    client = boto3.client("s3")


def _get_prefixes(bucket: str):
    prefixes = []
    # Since we don't know how many deployments we will encounter, its neccessary
    # to use a paginator object.  This is due to the 1000 key limit Boto3 imposes
    # on its responses. Each page will contain at metadata for a max of 1000 keys
    paginator = client.get_paginator("list_objects_v2")

    # There's no such thing as a directory in S3, only objects and their key, and prefixes.
    # As such to make this script managable in a high cardinality environment,
    # we want to leverage the S3 API to get a listing of all of the common prefixes.
    # This maps to what we logically think of as the deployment's directory.
    for page in paginator.paginate(Bucket=bucket, Delimiter="/"):
        prefixes.extend(page["CommonPrefixes"])

    # Now that we have our list of unique prefixes, lets clean up the formatting so
    # we can use this list later in the program.
    cleaned_prefixes = []
    for prefix in prefixes:
        cleaned_prefixes.append(prefix["Prefix"].strip("/"))

    return cleaned_prefixes


def _get_prefix_timestamp(prefix: str, bucket: str):

    result = client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    deployment_timestamp = result["Contents"][0]["LastModified"]

    return prefix, deployment_timestamp


def _get_prefix_list(prefix: str, bucket: str):
    # We use a paginator object because we don't know if the deployment will contain
    # 1000 or less files. In the event the deployment contains more than 1000 objects,
    # multiple pages of at most 1000 will be returned.
    paginator = client.get_paginator("list_objects_v2")
    keys = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for object in page["Contents"]:
            keys.append(object["Key"])

    return keys


def get_deployments(bucket: str):
    # This function returns a list of tuples containing the deployment name and its
    # timestamp. The timestamp used is that of a single file contained within a deployment
    prefixes = _get_prefixes(bucket)
    logger.debug(prefixes)
    deployments = []
    for prefix in prefixes:
        deployments.append(_get_prefix_timestamp(prefix, bucket))

    deployments.sort(key=lambda a: a[1])
    return deployments


def _delete_deployments(deployments_to_delete: list, bucket: str):
    logger.info(
        "The following {} deployments will be deleted:".format(
            (len(deployments_to_delete))
        )
    )
    for deployment in deployments_to_delete:
        logger.info(deployment[0] + " " + str(deployment[1]))
    # First we will make a list of all of the keys we will delete, then delete them.
    # Decoupling the code like this will make it a little easier to refactor using
    # async calls. This will dramatically speed up operation of the tool for high
    # cardinality deployment directories.
    keys_to_delete = []

    for deployment in deployments_to_delete:
        results = _get_prefix_list(deployment[0], bucket)
        keys_to_delete.extend(results)

    for key in keys_to_delete:
        response = client.delete_object(Bucket=bucket, Key=key)
        if response["ResponseMetadata"]["HTTPStatusCode"] is 204:
            logger.info("Succesfull deleted {}".format(key))

    return


def clean_deployments_time(bucket: str, date_time: str, deployments_to_keep:int):
    # This method glues together various internal and external methods
    # to deliver desired functinoality. This method is intended to be consumed by
    # a CLI or API framework.
    
    # Convert date_time into datetime object
    date_format = "%b %d %Y %H:%M"
    date_object = datetime.strptime(date_time, date_format)
    # Since AWS uses UTC will assume all datetimes entered are as well
    utc_date = date_object.replace(tzinfo=timezone.utc)
    # Get all deployments older than date_time
    deployments_to_delete = []

    deployments = get_deployments(bucket)
    logger.info("Found {} deployments in {}:".format(len(deployments), bucket))
    for deployment in deployments:
        logger.info(deployment[0] + " " + str(deployment[1]))
 
        if deployment[1] < utc_date:
            deployments_to_delete.append(deployment)
    # Since we previously sorted our array, we if we need to keep a few deployments
    # we can simply grab them from the end of the deployments_to_delete list populated
    # earlier in this method.
    deployments_remaining = (len(deployments) - len(deployments_to_delete))
    # If we are going to delete too many deployments, we will remove some from the deletion
    # list so we always retain `deployments_to_keep` deployments. 
    if  deployments_remaining < deployments_to_keep:

        deployments_to_rescue = deployments_to_keep - deployments_remaining
        deployments_to_delete_final = deployments_to_delete[:-deployments_to_rescue]
    else:
        deployments_to_delete_final = deployments_to_delete
    _delete_deployments(deployments_to_delete_final, bucket)

    return

def clean_deployments(bucket: str, X: int):
    # This method glues together various internal and external methods
    # to deliver desired functinoality. This method is intended to be consumed by
    # a CLI or API framework.

    # Get all deployments along with their timestamp
    deployments = get_deployments(bucket)
    logger.info("Found {} deployments in {}:".format(len(deployments), bucket))
    for deployment in deployments:
        logger.info(deployment[0] + " " + str(deployment[1]))
    # Create a new list containing only the deployments we will delete
    deployments_to_delete = deployments[int(X) :]
    _delete_deployments(deployments_to_delete, bucket)

    return
