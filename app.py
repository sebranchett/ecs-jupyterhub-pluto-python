#!/usr/bin/env python3
import yaml

from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
    aws_cognito as cognito,
    custom_resources as cr,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecr as ecr,
    App, CfnOutput, Stack, RemovalPolicy
)


class FrontEndStack(Stack):
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
        certificate_arn = config_yaml['certificate_arn']
        container_image_repository_arn = \
            config_yaml['container_image_repository_arn']
        container_image_tag = config_yaml['container_image_tag']

        suffix_txt = "secure"
        suffix = f'{suffix_txt}'.lower()

        vpc = ec2.Vpc(self, "VPC")

        data = open("./httpd.sh", "rb").read()
        httpd = ec2.UserData.for_linux()
        httpd.add_commands(str(data, 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            user_data=httpd,
        )

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

        certificate = acm.Certificate.from_certificate_arn(
            self, "Certificate", certificate_arn
        )
        listener = load_balancer.add_listener(
            f'{base_name}ServiceELBListener',
            port=443,
            protocol=elb.ApplicationProtocol.HTTPS,
            certificates=[certificate]
        )

        listener.add_targets(
            "Target", port=443,
            targets=[asg]
        )

        asg.scale_on_request_count(
            "AModestLoad", target_requests_per_minute=60
        )

        # User pool and user pool OAuth client
        cognito_user_pool = cognito.UserPool(
            self,
            f'{base_name}UserPool',
            removal_policy=RemovalPolicy.DESTROY,
            self_sign_up_enabled=False
        )

        cognito_user_pool_domain = cognito.UserPoolDomain(
            self,
            f'{base_name}UserPoolDomain',
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=application_prefix + '-' + suffix
            ),
            user_pool=cognito_user_pool
        )

        cognito_app_client = cognito.UserPoolClient(
            self,
            f'{base_name}UserPoolClient',
            user_pool=cognito_user_pool,
            generate_secret=True,
            supported_identity_providers=[
                cognito.UserPoolClientIdentityProvider.COGNITO],
            prevent_user_existence_errors=True,
            o_auth=cognito.OAuthSettings(
                callback_urls=[
                    'https://' + route53_record.domain_name +
                    '/hub/oauth_callback'
                ],
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True
                ),
                scopes=[cognito.OAuthScope.PROFILE, cognito.OAuthScope.OPENID]
            )
        )

        describe_cognito_user_pool_client = cr.AwsCustomResource(
            self,
            f'{base_name}UserPoolClientIDResource',
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_create=cr.AwsSdkCall(
                service='CognitoIdentityServiceProvider',
                action='describeUserPoolClient',
                parameters={
                    'UserPoolId': cognito_user_pool.user_pool_id,
                    'ClientId': cognito_app_client.user_pool_client_id
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    cognito_app_client.user_pool_client_id)
            )
        )

        cognito_user_pool_client_secret = \
            describe_cognito_user_pool_client.get_response_field(
                'UserPoolClient.ClientSecret'
            )

        # ECS task roles and definition
        ecs_task_execution_role = iam.Role(
            self, f'{base_name}TaskExecutionRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com')
        )

        managed_policy_arn = 'arn:aws:iam::aws:policy/service-role/' \
            'AmazonECSTaskExecutionRolePolicy'
        ecs_task_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self,
                f'{base_name}ServiceRole',
                managed_policy_arn=managed_policy_arn
            )
        )

        ecs_task_role = iam.Role(
            self,
            f'{base_name}TaskRole',
            assumed_by=iam.ServicePrincipal('ecs-tasks.amazonaws.com')
        )

        ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                resources=['*'],
                actions=['cloudwatch:PutMetricData', 'cloudwatch:ListMetrics']
            )
        )

        ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                resources=['*'],
                actions=[
                    'logs:CreateLogStream',
                    'logs:DescribeLogGroups',
                    'logs:DescribeLogStreams',
                    'logs:CreateLogGroup',
                    'logs:PutLogEvents',
                    'logs:PutRetentionPolicy'
                ]
            )
        )

        ecs_task_role.add_to_policy(
            iam.PolicyStatement(
                resources=['*'],
                actions=['ec2:DescribeRegions']
            )
        )

        ecs_task_definition = ecs.FargateTaskDefinition(
            self,
            f'{base_name}TaskDefinition',
            cpu=512,
            memory_limit_mib=2048,
            execution_role=ecs_task_execution_role,
            task_role=ecs_task_role
        )

        # ECS Container definition, service, target group and ALB attachment
        repository = ecr.Repository.from_repository_arn(
            self, "Repo", container_image_repository_arn
        )
        ecs_container = ecs_task_definition.add_container(
            f'{base_name}Container',
            image=ecs.ContainerImage.from_ecr_repository(
                repository=repository,
                tag=container_image_tag
            ),
            privileged=False,
            port_mappings=[
                ecs.PortMapping(
                    container_port=8000,
                    host_port=8000,
                    protocol=ecs.Protocol.TCP
                )
            ],
            logging=ecs.LogDriver.aws_logs(
                stream_prefix=f'{base_name}ContainerLogs-',
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                'OAUTH_CALLBACK_URL':
                    'https://' + route53_record.domain_name +
                    '/hub/oauth_callback',
                'OAUTH_CLIENT_ID': cognito_app_client.user_pool_client_id,
                'OAUTH_CLIENT_SECRET': cognito_user_pool_client_secret,
                'OAUTH_LOGIN_SERVICE_NAME':
                    config_yaml['oauth_login_service_name'],
                'OAUTH_LOGIN_USERNAME_KEY':
                    config_yaml['oauth_login_username_key'],
                'OAUTH_AUTHORIZE_URL':
                    'https://' + cognito_user_pool_domain.domain_name +
                    '.auth.' + self.region +
                    '.amazoncognito.com/oauth2/authorize',
                'OAUTH_TOKEN_URL':
                    'https://' + cognito_user_pool_domain.domain_name +
                    '.auth.' + self.region + '.amazoncognito.com/oauth2/token',
                'OAUTH_USERDATA_URL':
                    'https://' + cognito_user_pool_domain.domain_name +
                    '.auth.' + self.region +
                    '.amazoncognito.com/oauth2/userInfo',
                'OAUTH_SCOPE': ','.join(config_yaml['oauth_scope'])
            }
        )

        # ECS cluster
        ecs_cluster = ecs.Cluster(
            self, f'{base_name}Cluster',
            vpc=vpc
        )

        # Output the service URL to CloudFormation outputs
        CfnOutput(
            self,
            f'{base_name}HubURL',
            value='https://' + route53_record.domain_name
        )


app = App()
FrontEndStack(app, "FrontEndStack")
app.synth()
