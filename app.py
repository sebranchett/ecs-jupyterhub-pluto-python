#!/usr/bin/env python3
import os
import yaml

from aws_cdk import App, Environment

from HubStacks.frame_stack import FrameStack
from HubStacks.hub_stack import HubStack

default_env = Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"]
)

app = App()
config_yaml = yaml.load(
    open('config.yaml'), Loader=yaml.FullLoader)
frame = FrameStack(
    app, "FrameStack",
    config_yaml,
    env=default_env
)
HubStack(
    app, "HubStack",
    config_yaml,
    vpc=frame.vpc,
    load_balancer=frame.load_balancer,
    file_system=frame.file_system,
    ecs_service_security_group=frame.ecs_service_security_group,
    env=default_env
)

app.synth()
