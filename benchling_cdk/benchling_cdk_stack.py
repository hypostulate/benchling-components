import os

from aws_cdk import core as cdk
import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_events as events
import aws_cdk.aws_events_targets as targets

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core


class BenchlingCdkStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Set context (could be set in other ways)
        # See: https://docs.aws.amazon.com/cdk/latest/guide/context.html
        self.node.set_context("event_bus_arn", os.environ["EVENT_BUS_ARN"])
        self.node.set_context("benchling_url", os.environ["BENCHLING_URL"])
        self.node.set_context("benchling_api_key", os.environ["BENCHLING_API_KEY"])

        # Gather the Event Bus
        event_bus_arn = self.node.try_get_context("event_bus_arn")
        benchling_event_bus = events.EventBus.from_event_bus_arn(
            self,
            "BenchlingEventBus",
            event_bus_arn=event_bus_arn,
        )

        # Create the Lambda Function
        benchling_url = self.node.try_get_context("benchling_url")
        benchling_api_key = self.node.try_get_context("benchling_api_key")
        benchling_responsive_function = lambda_.Function(
            self,
            "BenchlingResponsiveFunction",
            # This code will build the dependencies from the requirements.txt
            # to construct the asset prior to upload
            code=lambda_.AssetCode(
                path="lambdas/log_entity_registered",
                bundling=core.BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_8.bundling_docker_image,
                    command=[
                        "bash", "-c",
                        "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output",
                    ],
                ),
            ),
            handler="app.lambda_handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            environment={
                "BENCHLING_URL": benchling_url,
                "BENCHLING_API_KEY": benchling_api_key,
            },
        )

        # Attach Events to the Lambda Function
        entity_registered_event = events.Rule(
            self,
            "EntityRegistrationEvent",
            event_bus = benchling_event_bus,
            event_pattern = events.EventPattern(
                detail_type = [
                    "v2.entity.registered"
                ],
            ),
            targets = [
                targets.LambdaFunction(
                    benchling_responsive_function
                )
            ]
        )
