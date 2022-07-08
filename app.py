#!/usr/bin/env python3
from aws_cdk import App

from HubStacks.data_stack import DataStack
from HubStacks.hub_stack import HubStack

app = App()
DataStack(app, "DataStack")
HubStack(app, "HubStack")

app.synth()
