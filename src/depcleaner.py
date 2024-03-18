import click
import logging
from backend.utils import (
    configureLogging,
)
from backend.deploy_cleaner import (
    clean_deployments,
    clean_deployments_time,
    get_deployments,
)

logger = logging.getLogger(__name__)


# This project uses click to parse CLI arguments and
# build the command layout.
#
# The method below is the main entrypoint for the cli tool
@click.group()
@click.pass_context
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["INFO", "DEBUG", "WARN", "ERROR"]),
)
@click.option("--log-destination", default="stdout")
@click.option(
    "--log-format",
    default="tab",
    type=click.Choice(["tab", "json"]),
)
def cli(
    ctx,
    log_level,
    log_destination,
    log_format,
):

    configureLogging(log_level, log_destination, log_format)


@cli.command()
@click.pass_context
@click.option(
    "--delete-older-than",
    "-X",
    type=int,
    envvar="DELETE_OLDER_THAN",
    required=True,
    help="In this mode the tool will delete all deployments older than the Xth oldest deployment",
)
@click.option(
    "--s3-bucket",
    "-s",
    required=True,
    help="S3 bucket containing Sure application deployments",
)
def keepx(ctx, delete_older_than, s3_bucket):
    logger.info("Cleaning up deployments older than top {}".format(delete_older_than))
    clean_deployments(s3_bucket, delete_older_than)


@cli.command()
@click.pass_context
@click.option(
    "--delete-older-than",
    "-X",
    type=str,
    envvar="DELETE_OLDER_THAN_TIME",
    required=True,
    help="In this mode the tool will delete all deployments older than X timestamp.",
)
@click.option(
    "--deployments-to-keep",
    "-Y",
    type=int,
    envvar="DEPLOYMENTS_TO_KEEP",
    required=True,
    help="Minimum number of deployments to keep regardless of timestamp.",
)
@click.option(
    "--s3-bucket",
    "-s",
    required=True,
    help="S3 bucket containing Sure application deployments",
)
def deleteafter(ctx, delete_older_than, deployments_to_keep, s3_bucket):
    logger.info(
        "Cleaning up deployments older than {}, while keeping minimum of {}".format(
            delete_older_than, deployments_to_keep
        )
    )
    clean_deployments_time(s3_bucket, delete_older_than, deployments_to_keep)


if __name__ == "main":
    cli()
