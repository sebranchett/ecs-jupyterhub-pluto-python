#!/usr/bin/env python3
import os

from aws_cdk import App, Environment

from HubStacks.frame_stack import FrameStack
from HubStacks.hub_stack import HubStack

default_env = Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"]
)

app = App()
frame = FrameStack(app, "FrameStack", env=default_env)
HubStack(
    app, "HubStack",
    vpc=frame.vpc,
    load_balancer=frame.load_balancer,
    file_system=frame.file_system,
    efs_security_group=frame.efs_security_group,
    ecs_service_security_group=frame.ecs_service_security_group,
    env=default_env
)

app.synth()
