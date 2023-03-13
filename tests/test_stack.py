#!/usr/bin/env python3
import yaml
from aws_cdk import App, Environment
from aws_cdk.assertions import Template

from HubStacks.frame_stack import FrameStack

app = App()
config_yaml = yaml.load(
    open('example_config.yaml'), Loader=yaml.FullLoader)

frame_stack = FrameStack(
    app, "test-frame-stack",
    config_yaml,
    env=Environment(
        account="123456789012", region="eu-central-1"
    )
)
template = Template.from_stack(frame_stack)


def test_synthesizes_properly():
    template.resource_count_is(type="AWS::EC2::VPC", count=1)
    template.resource_count_is(type="AWS::EC2::Subnet", count=4)
    template.resource_count_is(type="AWS::EC2::RouteTable", count=4)
    template.resource_count_is(
        type="AWS::EC2::SubnetRouteTableAssociation", count=4
    )
    template.resource_count_is(type="AWS::EC2::Route", count=4)
    template.resource_count_is(type="AWS::EC2::EIP", count=2)
    template.resource_count_is(type="AWS::EC2::NatGateway", count=2)
    template.resource_count_is(type="AWS::EC2::InternetGateway", count=1)
    template.resource_count_is(type="AWS::EC2::VPCGatewayAttachment", count=1)
    template.resource_count_is(type="AWS::EC2::SecurityGroup", count=3)


def test_vpc():
    template.has_resource_properties(
        type="AWS::EC2::VPC",
        props={"CidrBlock": "10.0.0.0/16",
               "EnableDnsHostnames": True,
               "EnableDnsSupport": True,
               "InstanceTenancy": "default",
               "Tags": [{
                    "Key": "Name",
                    "Value": "some-basenameVPC"
                }]
               }
    )
