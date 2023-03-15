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


def test_check_resource_counts():
    template.resource_count_is(type="Custom::AWS", count=2)
    template.resource_count_is(type="AWS::IAM::Policy", count=4)
    template.resource_count_is(type="AWS::IAM::Role", count=3)
    template.resource_count_is(type="AWS::ECS::Cluster", count=1)
    template.resource_count_is(type="AWS::ECS::Service", count=1)
    template.resource_count_is(type="AWS::ECS::TaskDefinition", count=3)
    template.resource_count_is(type="AWS::Logs::LogGroup", count=3)
    template.resource_count_is(type="AWS::EFS::AccessPoint", count=2)


def test_cognito_external_user():
    template.has_resource_properties(
        "Custom::AWS",
        {"Create": Match.string_like_regexp(".*adminCreateUser.*jupyter")}
    )


def test_single_user_task_definition():
    template.has_resource_properties(
        "AWS::ECS::TaskDefinition", {
            "ContainerDefinitions": Match.any_value(),
            "Cpu": Match.any_value(),
            "ExecutionRoleArn": Match.any_value(),
            "Memory": Match.any_value(),
            "NetworkMode": Match.string_like_regexp("awsvpc"),
            "RequiresCompatibilities": Match.any_value(),
            "TaskRoleArn": Match.any_value(),
            "Volumes": Match.any_value(),
        }
    )


def test_access_point():
    template.has_resource_properties(
        "AWS::EFS::AccessPoint", {
            "FileSystemId": Match.any_value(),
            "PosixUser": Match.any_value(),
            "RootDirectory": {
                "Path": Match.string_like_regexp("/jupyter"),
                "CreationInfo": {
                    "Permissions": Match.string_like_regexp("755")
                }
            }
        }
    )


def test_volume():
    template.has_resource_properties(
        "AWS::ECS::TaskDefinition", {
            "Volumes": [{
                "Name": Match.string_like_regexp(".*jupyter"),
                "EFSVolumeConfiguration": {
                    "AuthorizationConfig":
                        {"IAM": Match.string_like_regexp("ENABLED")},
                    "TransitEncryption": Match.string_like_regexp("ENABLED"),
                    "FilesystemId": Match.any_value()
                }
            }]
        }
    )


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
