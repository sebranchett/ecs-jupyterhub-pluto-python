# Configuration file for Jupyter Hub

import os
import sys
import re
import socket
from oauthenticator.generic import LocalGenericOAuthenticator
from fargatespawner import FargateSpawner, FargateSpawnerECSRoleAuthentication


join = os.path.join

here = os.path.dirname(__file__)
root = os.environ.get('OAUTHENTICATOR_DIR', here)
sys.path.insert(0, root)

c = get_config()

c.JupyterHub.log_level = 10

c.Authenticator.admin_users = admin = set()
with open(join(root, 'admins')) as f:
    for line in f:
        if not line:
            continue
        parts = line.split()
        name = parts[0]
        admin.add(name)

c.JupyterHub.authenticator_class = LocalGenericOAuthenticator
c.JupyterHub.shutdown_on_logout = True

c.OAuthenticator.oauth_callback_url = os.environ.get('OAUTH_CALLBACK_URL')
c.OAuthenticator.client_id = os.environ.get('OAUTH_CLIENT_ID')
c.OAuthenticator.client_secret = os.environ.get('OAUTH_CLIENT_SECRET')

allowed_users_string = os.environ.get('ALLOWED_USERS')
allowed_users = set(re.findall(r"'([^']*)'", allowed_users_string))
c.LocalGenericOAuthenticator.allowed_users = allowed_users

c.LocalGenericOAuthenticator.auto_login = True
c.LocalGenericOAuthenticator.create_system_users = True
c.LocalGenericOAuthenticator.add_user_cmd = [
    'adduser', '-q', '--gecos', '',
    '--home', '/home/$(echo USERNAME | sed "s/[@,.]/_/"g)',
    '--disabled-password', '--force-badname'
]

c.LocalGenericOAuthenticator.login_service = os.environ.get(
    'OAUTH_LOGIN_SERVICE_NAME'
)
c.LocalGenericOAuthenticator.username_key = os.environ.get(
    'OAUTH_LOGIN_USERNAME_KEY'
)
c.LocalGenericOAuthenticator.authorize_url = os.environ.get(
    'OAUTH_AUTHORIZE_URL'
)
c.LocalGenericOAuthenticator.token_url = os.environ.get(
    'OAUTH_TOKEN_URL'
)
c.LocalGenericOAuthenticator.userdata_url = os.environ.get(
    'OAUTH_USERDATA_URL'
)
c.LocalGenericOAuthenticator.scope = os.environ.get(
    'OAUTH_SCOPE'
).split(',')

# we need the hub to listen on all ips when it is in a container
c.JupyterHub.hub_ip = '0.0.0.0'

# c.JupyterHub.hub_connect_ip = socket.gethostbyname(socket.gethostname())

# c.JupyterHub.base_url = os.environ.get('FARGATE_BIND_URL')
# c.JupyterHub.bind_url = os.environ.get('FARGATE_BIND_URL')
# c.JupyterHub.hub_connect_url = os.environ.get('FARGATE_BIND_URL')
# c.JupyterHub.hub_bind_url = os.environ.get('FARGATE_BIND_URL')

c.Spawner.http_timeout = 180

c.JupyterHub.spawner_class = FargateSpawner
c.FargateSpawner.authentication_class = FargateSpawnerECSRoleAuthentication

c.FargateSpawner.aws_region = os.environ.get('FARGATE_SPAWNER_REGION')
c.FargateSpawner.aws_ecs_host = os.environ.get('FARGATE_SPAWNER_ECS_HOST')
c.FargateSpawner.notebook_port = 8888
c.FargateSpawner.notebook_scheme = "http"
# overrides ->containerOverrides -> command: '--config=notebook_config.py'
# 'containerOverrides': [{
#     'command': spawner.cmd + [
#         f'--port={spawner.notebook_port}',
#     ],
#     'environment': [
#         {
#             'name': name,
#             'value': value,
#         } for name, value in spawner.get_env().items()
#     ],
#     'name': 'jupyterhub-notebook',
# }],
c.FargateSpawner.get_run_task_args = lambda spawner: {
    'cluster': os.environ.get('FARGATE_SPAWNER_CLUSTER'),
    'taskDefinition': os.environ.get('FARGATE_SPAWNER_TASK_DEFINITION'),
    'overrides': {
        'taskRoleArn': os.environ.get('FARGATE_SPAWNER_TASK_ROLE_ARN'),
    },
    'count': 1,
    'launchType': 'FARGATE',
    'networkConfiguration': {
        'awsvpcConfiguration': {
            'assignPublicIp': 'DISABLED',
            'securityGroups':
                eval(os.environ.get('FARGATE_SPAWNER_SECURITY_GROUPS')),
            'subnets': eval(os.environ.get('FARGATE_SPAWNER_SUBNETS'))
        },
    },
}
