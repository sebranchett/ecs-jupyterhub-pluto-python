#!/usr/bin/env python3
import yaml

from aws_cdk import App, Environment
from aws_cdk.assertions import Template, Match

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


def test_synthesis_EC2_resources():
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


def test_synthesis_rest():
    template.resource_count_is(
        type="AWS::ElasticLoadBalancingV2::LoadBalancer", count=1
    )
    template.resource_count_is(type="AWS::Route53::RecordSet", count=1)
    template.resource_count_is(type="AWS::KMS::Key", count=1)
    template.resource_count_is(type="AWS::KMS::Alias", count=1)
    template.resource_count_is(type="AWS::EFS::FileSystem", count=1)
    template.resource_count_is(type="AWS::EFS::MountTarget", count=2)


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


def test_load_balancer():
    template.has_resource_properties(
        "AWS::ElasticLoadBalancingV2::LoadBalancer",
        {"Scheme": Match.string_like_regexp("internet-facing")}
    )


def test_file_system():
    template.has_resource_properties(
        "AWS::EFS::FileSystem",
        {"Encrypted": Match.exact(True)}
    )
    template.has_resource_properties(
        "AWS::EFS::FileSystem",
        {"KmsKeyId": Match.any_value()}
    )
    template.has_resource(
        "AWS::EFS::FileSystem",
        {"DeletionPolicy": Match.string_like_regexp("Delete")}
    )
    template.has_resource_properties(
        "AWS::EC2::SecurityGroup",
        {
            "GroupName": Match.string_like_regexp(".*EFSSG"),
            "SecurityGroupEgress": Match.any_value()
        }
    )
    template.has_resource(
        "AWS::KMS::Key",
        {"DeletionPolicy": Match.string_like_regexp("Delete")}
    )
