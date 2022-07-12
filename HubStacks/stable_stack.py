#!/usr/bin/env python3
import yaml

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_cognito as cognito,
    aws_efs as efs,
    aws_kms as kms,
    App, CfnOutput, Stack, RemovalPolicy
)


class StableStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        # General configuration variables
        config_yaml = yaml.load(
            open('config.yaml'), Loader=yaml.FullLoader)
        base_name = config_yaml["base_name"]
        domain_prefix = config_yaml['domain_prefix']
        application_prefix = 'pluto-' + domain_prefix
        hosted_zone_id = config_yaml['hosted_zone_id']
        hosted_zone_name = config_yaml['hosted_zone_name']

        vpc = ec2.Vpc(self, "VPC")

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

        # User pool and user pool OAuth client
        cognito_user_pool = cognito.UserPool(
            self,
            f'{base_name}UserPool',
            removal_policy=RemovalPolicy.DESTROY,
            self_sign_up_enabled=False
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

        CfnOutput(
            self,
            f'{base_name}_cognito_user_pool_id',
            value=cognito_user_pool.user_pool_id
        )

        CfnOutput(
            self,
            f'{base_name}_cognito_user_pool_arn',
            value=cognito_user_pool.user_pool_arn,
            export_name=f'{base_name}_cognito_user_pool_arn'
        )

        CfnOutput(
            self,
            f'{base_name}_load_balancer_arn',
            value=load_balancer.load_balancer_arn,
            export_name=f'{base_name}_load_balancer_arn'
        )

        CfnOutput(
            self,
            f'{base_name}_file_system_arn',
            value=file_system.file_system_arn,
            export_name=f'{base_name}_file_system_arn'
        )
