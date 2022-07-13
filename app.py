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
FrameStack(app, "FrameStack", env=default_env)
HubStack(app, "HubStack", env=default_env)

app.synth()
