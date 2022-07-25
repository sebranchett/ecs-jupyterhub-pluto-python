#!/usr/bin/env python3
import yaml

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
    def __init__(self, app: App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # General configuration variables
        config_yaml = yaml.load(
            open('config.yaml'), Loader=yaml.FullLoader)
        base_name = config_yaml["base_name"]
        domain_prefix = config_yaml['domain_prefix']
        application_prefix = 'pluto-' + domain_prefix
        hosted_zone_id = config_yaml['hosted_zone_id']
        hosted_zone_name = config_yaml['hosted_zone_name']

        vpc = ec2.Vpc(self, "VPC", max_azs=2)

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

        # Output the service URL to CloudFormation outputs
        CfnOutput(
            self,
            f'{base_name}HubURL',
            value='https://' + route53_record.domain_name
        )

        # Define this hear to prevent cyclic reference
        ecs_service_security_group = ec2.SecurityGroup(
            self,
            f'{base_name}ServiceSG',
            vpc=vpc,
            description='Hub ECS service containers security group',
            allow_all_outbound=True
        )

        # Output resources needed by HubStack
        self.vpc = vpc
        self.load_balancer = load_balancer
        self.file_system = file_system
        self.efs_security_group = efs_security_group
        self.ecs_service_security_group = ecs_service_security_group
