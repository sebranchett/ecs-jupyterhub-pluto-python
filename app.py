#!/usr/bin/env python3
from aws_cdk import App

from HubStacks.stable_stack import StableStack
from HubStacks.hub_stack import HubStack

app = App()
StableStack(app, "StableStack")
HubStack(app, "HubStack")

app.synth()
