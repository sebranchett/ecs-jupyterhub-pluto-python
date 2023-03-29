#!/usr/bin/env python3

from aws_cdk import (
    aws_elasticloadbalancingv2 as elb,
    aws_certificatemanager as acm,
    custom_resources as cr,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_logs as logs,
    aws_ecr as ecr,
    aws_efs as efs,
    App, Stack, Environment
)
from cognito_tudelft.tudelft_idp import CognitoTudelftStack


class HubStack(Stack):
    """
    Create a Fargate JupyterHub service that spawns single user Fargate
    containers. Users can authenticate through native Cognito or the TU Delft
    identity provider. EFS is used to provide persistent storage of the users'
    /home/jovyan/work directory.
    Adds:
    - CognitoTudelftStack
    - ECS cluster with JupyterHub service
    - JupyterHub Fargate task definition
    - Single user Fargate task definition for each admin/allowed user
    - IAM roles and policies
    ------
    Inputs
    ------
    - config_yaml: str -
        name of yaml file containing configuration
    - vpc: Vpc -
        a VPC for the application
    - load_balancer: ApplicationLoadBalancer -
        an application load balancer for the application
    - file_system: FileSystem -
        a file system for persistent storage of user data
    - ecs_service_security_group: SecurityGroup
        a security group for an ECS service that allows for communication
        between containers of the service
    ----------------------------
    Inputs from config.yaml file
    ----------------------------
    Inputs are read from a config.yaml file:
    - base_name: base name to be used in the Stacks
    - certificate_arn: ARN of the managed certificate for the domain name
    - cognito_user_pool_id: ID of the (empty) cognito user pool to use
    - domain_prefix: text to add after 'pluto-' and before domain name
    - hosted_zone_name: name of the AWS Hosted Zone
    - hub_container_image_repository_arn: ARN of the ECR for the JupyterHub
      image
    - hub_container_image_tag: tag for the JupyterHub image
    - num_containers: the desired number of JupyterHub service containers
    - oauth_login_username_key: key of field to use as username, either
      'preferred_username' (NedID) or 'email'
    - oauth_login_service_name: a name for the Cognito login service
    - oauth_scope: list of oauth scopes
    - single_user_container_image_repository_arn: ARN of the ECR for the
      single user image
    - single_user_container_image_tag: tag for the single user image
    - temp_password: password given to non TU Delft users. They will be
      required to change this the first time they log in

    -----------------------
    Inputs from admins file
    -----------------------
    List of admin usernames, one per line in plane text file called 'admins'

    ------------------------------
    Inputs from allowed_users file
    ------------------------------
    List of regular user usernames, one per line in plane text file
    called 'allowed_users'
    """

    def __init__(
        self, app: App, id: str,
        config_yaml, vpc, load_balancer, file_system,
        ecs_service_security_group, **kwargs
    ) -> None:
        super().__init__(app, id, **kwargs)

        # General configuration variables
        base_name = config_yaml["base_name"]
        cognito_user_pool_id = config_yaml['cognito_user_pool_id']
        domain_prefix = config_yaml['domain_prefix']
        application_prefix = 'pluto-' + domain_prefix
        certificate_arn = config_yaml['certificate_arn']
        hub_container_image_repository_arn = \
            config_yaml['hub_container_image_repository_arn']
        hub_container_image_tag = config_yaml['hub_container_image_tag']
        single_user_container_image_repository_arn = \
            config_yaml['single_user_container_image_repository_arn']
        single_user_container_image_tag = \
            config_yaml['single_user_container_image_tag']
        hosted_zone_name = config_yaml['hosted_zone_name']

        domain_name = application_prefix + '.' + hosted_zone_name

        # JupyterHub admin users from file
        admin_users = set()
        try:
            with open('hub_docker/admins') as fp:
                for line in fp:
                    if not line:
                        continue
                    admin_users.add(line.strip())
        except IOError:
            pass

        # JupyterHub allowed users from file
        allowed_users = set()
        try:
            with open('hub_docker/allowed_users') as fp:
                for line in fp:
                    if not line:
                        continue
                    allowed_users.add(line.strip())
        except IOError:
            pass

        # Find all the non TU Delft (external) users
        all_users = admin_users | allowed_users
        external_users = set()
        for user in all_users:
            if not user.endswith("tudelft.nl"):
                external_users.add(user)

        # Set up a Cognito Stack for TU Delft authentication
        cognito_tudelft_stack = CognitoTudelftStack(
            self,
            "CognitoTudelftStack",
            base_name=base_name,
            application_domain_name=domain_name,
            cognito_user_pool_id=cognito_user_pool_id,
            env=Environment(
                account=self.account,
                region=self.region
            ),
        )

        describe_cognito_user_pool_client = cr.AwsCustomResource(
            self,
            f'{base_name}UserPoolClientIDResource',
            install_latest_aws_sdk=False,
            log_retention=logs.RetentionDays.ONE_WEEK,
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
            on_create=cr.AwsSdkCall(
                service='CognitoIdentityServiceProvider',
                action='describeUserPoolClient',
                parameters={
                    'UserPoolId': cognito_user_pool_id,
                    'ClientId': cognito_tudelft_stack.app_client.
                        user_pool_client_id
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    cognito_tudelft_stack.app_client.user_pool_client_id)
            )
        )

        cognito_user_pool_client_secret = \
            describe_cognito_user_pool_client.get_response_field(
                'UserPoolClient.ClientSecret'
            )

        # Use the Cognito identity provider for non TU Delft users
        user_index = 0
        for user in external_users:
            user_index += 1
            cr.AwsCustomResource(
                self,
                f'{base_name}UserPoolUser'+str(user_index),
                install_latest_aws_sdk=False,
                log_retention=logs.RetentionDays.ONE_WEEK,
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                    resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE),
                on_create=cr.AwsSdkCall(
                    service='CognitoIdentityServiceProvider',
                    action='adminCreateUser',
                    parameters={
                        'UserPoolId': cognito_user_pool_id,
                        'Username': user,
                        'TemporaryPassword': config_yaml[
                            'temp_password'
                        ],
                        'UserAttributes': [
                            {
                                'Name': 'preferred_username',
                                'Value': user
                            }
                        ]
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(
                        cognito_user_pool_id)
                ),
                on_delete=cr.AwsSdkCall(
                    service='CognitoIdentityServiceProvider',
                    action='adminDeleteUser',
                    parameters={
                        'UserPoolId': cognito_user_pool_id,
                        'Username': user
                    },
                    physical_resource_id=cr.PhysicalResourceId.of(
                        cognito_user_pool_id)
                )
            )

        # ECS task roles
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

        ecs_task_execution_role.add_to_policy(
            iam.PolicyStatement(
                resources=['*'],
                actions=[
                    'iam:PassRole'
                ]
            )
        )

        ecs_task_execution_role.add_to_policy(
            iam.PolicyStatement(
                resources=[file_system.file_system_arn],
                actions=[
                    'elasticfilesystem:ClientRootAccess',
                    'elasticfilesystem:ClientWrite',
                    'elasticfilesystem:ClientMount'
                ]
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
                actions=[
                    'logs:CreateLogStream',
                    'logs:DescribeLogGroups',
                    'logs:DescribeLogStreams',
                    'logs:CreateLogGroup',
                    'logs:PutLogEvents',
                    'logs:PutRetentionPolicy',
                    'ecs:RunTask',
                    'ecs:StopTask',
                    'ecs:DescribeTasks',
                    'iam:PassRole',
                    'cloudwatch:PutMetricData',
                    'cloudwatch:ListMetrics',
                    'ec2:DescribeRegions'
                ]
            )
        )

        # ECS cluster with service, Hub task and JupyterHub admin/user tasks
        ecs_cluster = ecs.Cluster(
            self, f'{base_name}Cluster',
            vpc=vpc
        )

        # single user container task definition
        single_user_repository = ecr.Repository.from_repository_arn(
            self, "SingleUserRepo",
            single_user_container_image_repository_arn
        )

        task_definitions = {}
        for user in all_users:
            username = user.replace("@", "_").replace(".", "_")

            single_user_task_definition = ecs.FargateTaskDefinition(
                self, username + "TaskDef",
                cpu=512,
                memory_limit_mib=4096,
                execution_role=ecs_task_execution_role,
                task_role=ecs_task_role
            )

            single_user_access_pt = efs.AccessPoint(
                self, username + "AccessPt",
                file_system=file_system,
                create_acl=efs.Acl(
                    owner_gid="100",
                    owner_uid="1000",
                    permissions="755"
                ),
                path="/" + username,
                posix_user=efs.PosixUser(
                    gid="100",
                    uid="1000"
                )
            )

            single_user_container = single_user_task_definition.add_container(
                "SingleUserContainer",
                image=ecs.ContainerImage.from_ecr_repository(
                    repository=single_user_repository,
                    tag=single_user_container_image_tag
                ),
                privileged=False,
                port_mappings=[
                    ecs.PortMapping(container_port=8888)
                ],
                logging=ecs.LogDrivers.aws_logs(
                    stream_prefix=f'{base_name}SingleUser-',
                    log_retention=logs.RetentionDays.ONE_WEEK
                )
            )

            # Add personal storage
            single_user_task_definition.add_volume(
                name='efs-' + username + '-volume',
                efs_volume_configuration=ecs.EfsVolumeConfiguration(
                    file_system_id=file_system.file_system_id,
                    authorization_config=ecs.AuthorizationConfig(
                        access_point_id=single_user_access_pt.access_point_id,
                        iam="ENABLED"
                    ),
                    transit_encryption="ENABLED"
                )
            )

            single_user_container.add_mount_points(ecs.MountPoint(
                container_path='/home/jovyan/work',
                source_volume='efs-' + username + '-volume',
                read_only=False
            ))

            # Add read only access to storage owned by admins
            if user in admin_users:
                read_only = False
            else:
                read_only = True

            single_user_task_definition.add_volume(
                name='efs-reference-volume',
                efs_volume_configuration=ecs.EfsVolumeConfiguration(
                    file_system_id=file_system.file_system_id,
                    authorization_config=ecs.AuthorizationConfig(
                        access_point_id=single_user_access_pt.access_point_id,
                        iam="ENABLED"
                    ),
                    transit_encryption="ENABLED"
                )
            )

            single_user_container.add_mount_points(ecs.MountPoint(
                container_path='/home/jovyan/reference',
                source_volume='efs-reference-volume',
                read_only=read_only
            ))

            task_definitions[user] = \
                single_user_task_definition.task_definition_arn

        # JupyterHub hub task definition
        hub_task_definition = ecs.FargateTaskDefinition(
            self,
            f'{base_name}TaskDefinition',
            cpu=512,
            memory_limit_mib=1024,
            execution_role=ecs_task_execution_role,
            task_role=ecs_task_role
        )

        hub_repository = ecr.Repository.from_repository_arn(
            self, "Repo", hub_container_image_repository_arn
        )

        # Make a string of the private subnets
        subnet_ids = []
        for subnet in vpc.private_subnets:
            subnet_ids.append(subnet.subnet_id)

        # Make a string of the security group ids
        security_group_ids = []
        security_group_ids.append(ecs_service_security_group.security_group_id)

        hub_container = hub_task_definition.add_container(
            f'{base_name}Container',
            image=ecs.ContainerImage.from_ecr_repository(
                repository=hub_repository,
                tag=hub_container_image_tag
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
                stream_prefix=f'{base_name}Hub-',
                log_retention=logs.RetentionDays.ONE_WEEK
            ),
            environment={
                'ADMIN_USERS': str(admin_users),
                'ALLOWED_USERS': str(all_users),
                'OAUTH_CALLBACK_URL':
                    'https://' + domain_name +
                    '/hub/oauth_callback',
                'OAUTH_CLIENT_ID': cognito_tudelft_stack.app_client.
                    user_pool_client_id,
                'OAUTH_CLIENT_SECRET': cognito_user_pool_client_secret,
                'OAUTH_LOGIN_SERVICE_NAME':
                    config_yaml['oauth_login_service_name'],
                'OAUTH_LOGIN_USERNAME_KEY':
                    config_yaml['oauth_login_username_key'],
                'OAUTH_AUTHORIZE_URL':
                    'https://' +
                    cognito_tudelft_stack.user_pool_domain.domain_name +
                    '.auth.' + self.region +
                    '.amazoncognito.com/oauth2/authorize',
                'OAUTH_TOKEN_URL':
                    'https://' +
                    cognito_tudelft_stack.user_pool_domain.domain_name +
                    '.auth.' + self.region + '.amazoncognito.com/oauth2/token',
                'OAUTH_USERDATA_URL':
                    'https://' +
                    cognito_tudelft_stack.user_pool_domain.domain_name +
                    '.auth.' + self.region +
                    '.amazoncognito.com/oauth2/userInfo',
                'OAUTH_SCOPE': ','.join(config_yaml['oauth_scope']),
                'FARGATE_HUB_CONNECT_IP':
                    f'{base_name}Container',
                'FARGATE_SPAWNER_REGION':
                    self.region,
                'FARGATE_SPAWNER_ECS_HOST':
                    'ecs.' + self.region + '.amazonaws.com',
                'FARGATE_SPAWNER_CLUSTER':
                    ecs_cluster.cluster_name,
                'FARGATE_SPAWNER_TASK_DEFINITIONS':
                    str(task_definitions),
                'FARGATE_SPAWNER_TASK_ROLE_ARN':
                    ecs_task_role.role_arn,
                'FARGATE_SPAWNER_SECURITY_GROUPS':
                    str(security_group_ids),
                'FARGATE_SPAWNER_SUBNETS':
                    str(subnet_ids),
                'FARGATE_SPAWNER_CONTAINER_NAME':
                    "SingleUserContainer",
                'FARGATE_EFS_ID': file_system.file_system_id
            }
        )

        hub_task_definition.add_volume(
            name='efs-hub-volume',
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id
            )
        )

        hub_container.add_mount_points(ecs.MountPoint(
            container_path='/home',
            source_volume='efs-hub-volume',
            read_only=False
        ))

        # Create the JupyterHub service
        hub_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, f'{base_name}HubService',
            cluster=ecs_cluster,
            task_definition=hub_task_definition,
            load_balancer=load_balancer,
            desired_count=config_yaml['num_containers'],
            security_groups=[ecs_service_security_group],
            open_listener=False,
            enable_ecs_managed_tags=True
        )

        hub_service.target_group.configure_health_check(
            path='/hub',
            enabled=True,
            healthy_http_codes='200-302'
        )

        certificate = acm.Certificate.from_certificate_arn(
            self, "Certificate", certificate_arn
        )
        load_balancer.add_listener(
            f'{base_name}HubServiceListener',
            port=443,
            protocol=elb.ApplicationProtocol.HTTPS,
            certificates=[certificate],
            default_action=elb.ListenerAction.forward(
                target_groups=[hub_service.target_group])
        )
