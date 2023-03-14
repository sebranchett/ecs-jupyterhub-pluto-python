#!/usr/bin/env python3

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_efs as efs,
    aws_kms as kms,
    App, CfnOutput, Stack, RemovalPolicy
)


class FrameStack(Stack):
    """
    Create a frame for an application to communicate with the outside world.
    Adds:
    - VPC
    - Application Load Balancer
    - Route53 A record
    - EFS file system for persistent storage
    - Security group for an ECS service, allowing internal communication
    ...
    Inputs
    ------
    Inputs are read from a config.yaml file:
    - hosted_zone_id: ID of an AWS Hosted Zone
    - hosted_zone_name: name of the AWS Hosted Zone
    - base_name: base name to be used in the Stacks
    - domain_prefix: domain prefix for the application
    - num_azs: number of Availability Zones to user (must be 2 or more)
    ...
    Attributes
    ----------
    vpc : Vpc
        a VPC for the application
    load_balancer : ApplicationLoadBalancer
        an application load balancer for the application
    file_system : FileSystem
        a file system for persistent storage of user data
    efs_security_group : SecurityGroup
        a security group for the file system that allows user access and
        implements encryption at rest and in transit
    ecs_service_security_group : SecurityGroup
        a security group for an ECS service that allows for communication
        between containers of the service
    """

    def __init__(self, app: App, id: str, config_yaml, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # General configuration variables
        base_name = config_yaml["base_name"]
        domain_prefix = config_yaml['domain_prefix']
        application_prefix = 'pluto-' + domain_prefix
        hosted_zone_id = config_yaml['hosted_zone_id']
        hosted_zone_name = config_yaml['hosted_zone_name']
        # number of Availability Zones must be 2 or more for load balancing
        num_azs = config_yaml['num_azs']

        # An AWS Hosted Zone must already exist and
        # it's ID and name must be specified in the config_yaml.

        vpc = ec2.Vpc(self, "VPC", max_azs=num_azs, vpc_name=f'{base_name}VPC')

        load_balancer = elb.ApplicationLoadBalancer(
            self, f'{base_name}LoadBalancer',
            vpc=vpc,
            internet_facing=True
        )

        hosted_zone = \
            route53.PublicHostedZone.from_hosted_zone_attributes(
                self,
                f'{base_name}HostedZone',
                hosted_zone_id=hosted_zone_id,
                zone_name=hosted_zone_name
            )

        route53_record = route53.ARecord(
            self,
            f'{base_name}ELBRecord',
            zone=hosted_zone,
            record_name=application_prefix,
            target=route53.RecordTarget(alias_target=(
                route53_targets.LoadBalancerTarget(
                    load_balancer=load_balancer)))
        )

        # EFS FileSystem
        efs_security_group = ec2.SecurityGroup(
            self,
            f'{base_name}EFSSG',
            security_group_name=f'{base_name}EFSSG',
            vpc=vpc,
            description='Shared filesystem security group',
            allow_all_outbound=True
        )

        efs_cmk = kms.Key(
            self,
            f'{base_name}EFSCMK',
            alias='ecs-efs-cmk',
            description='CMK for EFS Encryption',
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        file_system = efs.FileSystem(
            self,
            f'{base_name}EFS',
            vpc=vpc,
            security_group=efs_security_group,
            encrypted=True,
            kms_key=efs_cmk,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Define ECS service security group here to prevent cyclic reference
        ecs_service_security_group = ec2.SecurityGroup(
            self,
            f'{base_name}ServiceSG',
            vpc=vpc,
            description='Hub ECS service containers security group',
            allow_all_outbound=True
        )
        # Allow internal communication between containers
        ecs_service_security_group.connections.allow_internally(
            port_range=ec2.Port.all_traffic()
        )
        # All access between EFS and ECS service containers
        efs_security_group.connections.allow_from(
            ecs_service_security_group,
            port_range=ec2.Port.tcp(2049),
            description='Allow EFS from ECS Service containers'
        )

        # Output the service URL to CloudFormation outputs
        CfnOutput(
            self,
            f'{base_name}HubURL',
            value='https://' + route53_record.domain_name
        )

        # Output resources needed by HubStack
        self.vpc = vpc
        self.load_balancer = load_balancer
        self.file_system = file_system
        self.efs_security_group = efs_security_group
        self.ecs_service_security_group = ecs_service_security_group
