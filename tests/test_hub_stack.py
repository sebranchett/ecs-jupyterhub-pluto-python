#!/usr/bin/env python3
import yaml

from aws_cdk import App, Environment, RemovalPolicy
from aws_cdk.assertions import Template, Match

from HubStacks.frame_stack import FrameStack
from HubStacks.hub_stack import HubStack

app = App()
config_yaml = yaml.load(
    open('example_config.yaml'), Loader=yaml.FullLoader)

frame = FrameStack(
    app, "FrameStack",
    config_yaml,
    env=Environment(
        account="123456789012", region="eu-central-1"
    )
)
hub_stack = HubStack(
    app, "HubStack",
    config_yaml,
    vpc=frame.vpc,
    load_balancer=frame.load_balancer,
    file_system=frame.file_system,
    efs_security_group=frame.efs_security_group,
    ecs_service_security_group=frame.ecs_service_security_group,
    env=Environment(
        account="123456789012", region="eu-central-1"
    )
)
template = Template.from_stack(hub_stack)


def test_synthesis_EC2_resources():
    template.resource_count_is(type="Custom::AWS", count=2)
    template.resource_count_is(type="AWS::IAM::Policy", count=4)
    template.resource_count_is(type="AWS::IAM::Role", count=3)
    template.resource_count_is(type="AWS::ECS::Cluster", count=1)
    template.resource_count_is(type="AWS::ECS::Service", count=1)
    template.resource_count_is(type="AWS::ECS::TaskDefinition", count=3)
    template.resource_count_is(type="AWS::Logs::LogGroup", count=3)
    template.resource_count_is(type="AWS::EFS::AccessPoint", count=2)


# def test_file_system():
#     template.has_resource_properties(
#         "AWS::EFS::FileSystem",
#         {"Encrypted": Match.exact(True)}
#     )
#     template.has_resource_properties(
#         "AWS::EFS::FileSystem",
#         {"KmsKeyId": Match.any_value()}
#     )
#     template.has_resource(
#         "AWS::EFS::FileSystem",
#         {"DeletionPolicy": Match.string_like_regexp("Delete")}
#     )
