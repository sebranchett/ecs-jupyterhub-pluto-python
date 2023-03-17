#!/usr/bin/env python3
import yaml

from aws_cdk import App, Environment
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
    template.resource_count_is(type="AWS::IAM::Policy", count=5)
    template.resource_count_is(type="AWS::IAM::Role", count=4)
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


def test_single_user_container():
    template.has_resource_properties(
        "AWS::ECS::TaskDefinition", {
            "ContainerDefinitions": [{
                "Image": Match.any_value(),
                "Privileged": Match.exact(False),
                "PortMappings": [{
                    "ContainerPort": Match.exact(8888)
                }],
                "LogConfiguration": {
                    "Options": {
                        "awslogs-stream-prefix":
                            Match.string_like_regexp(".*SingleUser")
                    }
                },
                "MountPoints": Match.any_value()
            }]
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


def test_mount_point():
    template.has_resource_properties(
        "AWS::ECS::TaskDefinition", {
            "ContainerDefinitions": [{
                "MountPoints": [{
                    "ContainerPath":
                        Match.string_like_regexp("/home/jovyan/work"),
                    "ReadOnly": Match.exact(False),
                    "SourceVolume": Match.string_like_regexp(".*jupyter")
                }]
            }]
        }
    )


def test_hub_task_definition():
    template.has_resource_properties(
        "AWS::ECS::TaskDefinition", {
            "ContainerDefinitions": Match.any_value(),
            "Cpu": Match.any_value(),
            "ExecutionRoleArn": Match.any_value(),
            "Memory": Match.any_value(),
            "TaskRoleArn": Match.any_value(),
            "Volumes": [{
                "Name": Match.string_like_regexp("efs-hub"),
            }]
        }
    )


def test_hub_container():
    template.has_resource_properties(
        "AWS::ECS::TaskDefinition", {
            "ContainerDefinitions": [{
                "Image": Match.any_value(),
                "Privileged": Match.exact(False),
                "PortMappings": [{
                    "ContainerPort": Match.exact(8000)
                }],
                "LogConfiguration": {
                    "Options": {
                        "awslogs-stream-prefix":
                            Match.string_like_regexp(".*Hub-")
                    }
                },
                "MountPoints": Match.any_value(),
                "Environment": [{
                    "Name": Match.string_like_regexp("ADMIN_USERS")
                }, {
                    "Name": Match.string_like_regexp("ALLOWED_USERS")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_CALLBACK_URL")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_CLIENT_ID")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_CLIENT_SECRET")
                }, {
                    "Name":
                        Match.string_like_regexp("OAUTH_LOGIN_SERVICE_NAME")
                }, {
                    "Name":
                        Match.string_like_regexp("OAUTH_LOGIN_USERNAME_KEY")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_AUTHORIZE_URL")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_TOKEN_URL")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_USERDATA_URL")
                }, {
                    "Name": Match.string_like_regexp("OAUTH_SCOPE")
                }, {
                    "Name": Match.string_like_regexp("FARGATE_HUB_CONNECT_IP")
                }, {
                    "Name": Match.string_like_regexp("FARGATE_SPAWNER_REGION")
                }, {
                    "Name":
                        Match.string_like_regexp("FARGATE_SPAWNER_ECS_HOST")
                }, {
                    "Name": Match.string_like_regexp("FARGATE_SPAWNER_CLUSTER")
                }, {
                    "Name": Match.
                        string_like_regexp("FARGATE_SPAWNER_TASK_DEFINITIONS")
                }, {
                    "Name": Match.
                        string_like_regexp("FARGATE_SPAWNER_TASK_ROLE_ARN")
                }, {
                    "Name": Match.
                        string_like_regexp("FARGATE_SPAWNER_SECURITY_GROUPS")
                }, {
                    "Name": Match.string_like_regexp("FARGATE_SPAWNER_SUBNETS")
                }, {
                    "Name": Match.
                        string_like_regexp("FARGATE_SPAWNER_CONTAINER_NAME")
                }, {
                    "Name": Match.string_like_regexp("FARGATE_EFS_ID")
                }]
            }]
        }
    )


def test_hub_service():
    template.has_resource_properties(
        "AWS::ECS::Service", {
            "Cluster": Match.any_value(),
            "TaskDefinition": Match.any_value(),
            "LoadBalancers": [{"ContainerPort": Match.exact(8000)}],
            "DesiredCount": Match.any_value(),
            "NetworkConfiguration": {
                "AwsvpcConfiguration": {
                    "SecurityGroups": Match.any_value()
                }
            }
        }
    )


def test_role():
    # TaskExecutionRole
    template.has_resource_properties(
        "AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {"Statement": [{"Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            }}]},
            "ManagedPolicyArns": [Match.string_like_regexp("arn.*")]
        }
    )
    # TaskRole
    template.has_resource_properties(
        "AWS::IAM::Role", {
            "AssumeRolePolicyDocument": {"Statement": [{"Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            }}]},
            "ManagedPolicyArns": [Match.not_("arn.*")]
        }
    )


def test_policy():
    # TaskExecutionRole policy
    template.has_resource_properties(
        "AWS::IAM::Policy", {
            "PolicyDocument": {"Statement": [
                {"Action": "iam:PassRole"},
                {"Action": [
                    "elasticfilesystem:ClientRootAccess",
                    "elasticfilesystem:ClientWrite",
                    "elasticfilesystem:ClientMount"
                ]},
                {"Action": [
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage"
                ]},
                {"Action": "ecr:GetAuthorizationToken"},
                {"Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]},
                {"Action": Match.any_value()},
                {"Action": Match.any_value()}
            ]}
        }
    )

    # TaskRole policy
    template.has_resource_properties(
        "AWS::IAM::Policy", {
            "PolicyDocument": {"Statement": [{"Action": [
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:CreateLogGroup",
                "logs:PutLogEvents",
                "logs:PutRetentionPolicy",
                "ecs:RunTask",
                "ecs:StopTask",
                "ecs:DescribeTasks",
                "iam:PassRole",
                "cloudwatch:PutMetricData",
                "cloudwatch:ListMetrics",
                "ec2:DescribeRegions"
            ]}]}
        }
    )
