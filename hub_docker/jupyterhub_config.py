# Configuration file for Jupyter Hub

import os
import sys
from oauthenticator.generic import LocalGenericOAuthenticator
from fargatespawner import FargateSpawner, FargateSpawnerECSRoleAuthentication
from jupyter_client.localinterfaces import public_ips


join = os.path.join

here = os.path.dirname(__file__)
root = os.environ.get('OAUTHENTICATOR_DIR', here)
sys.path.insert(0, root)

c = get_config()

c.JupyterHub.log_level = 10

c.Authenticator.admin_users = eval(os.environ.get('ADMIN_USERS'))

c.JupyterHub.authenticator_class = LocalGenericOAuthenticator
c.JupyterHub.shutdown_on_logout = True

c.OAuthenticator.oauth_callback_url = os.environ.get('OAUTH_CALLBACK_URL')
c.OAuthenticator.client_id = os.environ.get('OAUTH_CLIENT_ID')
c.OAuthenticator.client_secret = os.environ.get('OAUTH_CLIENT_SECRET')

c.LocalGenericOAuthenticator.allowed_users = eval(
    os.environ.get('ALLOWED_USERS')
)

c.LocalGenericOAuthenticator.auto_login = True
c.LocalGenericOAuthenticator.create_system_users = True
c.LocalGenericOAuthenticator.add_user_cmd = [
    'adduser', '-q', '--gecos', '""',
    '--home', '$(echo /home/USERNAME | sed "s/[@,.]/_/"g)',
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
# this from: https://github.com/jupyterhub/dockerspawner/issues/198
# "nils-werner commented on Jul 12, 2018"
ip = public_ips()[0]
# Users from outside hitting the proxy:
c.JupyterHub.ip = ip
c.JupyterHub.port = 8000
# API side of proxy, that the Hub will use:
c.ConfigurableHTTPProxy.api_url = 'http://' + ip + ':8001'
# Hub location so the proxy and the spawners can find it
# --default-target and --error-target should point here
c.JupyterHub.hub_ip = ip
c.JupyterHub.hub_port = 8081
# the hostname/ip that should be used to connect to the hub
c.JupyterHub.hub_connect_ip = ip

c.Spawner.start_timeout = 180
c.Spawner.http_timeout = 180
c.Spawner.ip = '0.0.0.0'
c.Spawner.port = 8888

c.JupyterHub.spawner_class = FargateSpawner
c.FargateSpawner.authentication_class = FargateSpawnerECSRoleAuthentication

c.FargateSpawner.aws_region = os.environ.get('FARGATE_SPAWNER_REGION')
c.FargateSpawner.aws_ecs_host = os.environ.get('FARGATE_SPAWNER_ECS_HOST')
c.FargateSpawner.notebook_port = 8888
c.FargateSpawner.notebook_scheme = "http"
# #PATH seems to get mangled when starting a single user container from
# jupyterhub container. /opt/conda/bin does not appear and this is
# exactly what is needed for the command jupyterhub-singleuser
task_definition_arns = eval(os.environ.get('FARGATE_SPAWNER_TASK_DEFINITIONS'))

c.FargateSpawner.get_run_task_args = lambda spawner: {
    'cluster': os.environ.get('FARGATE_SPAWNER_CLUSTER'),
    'taskDefinition':
        task_definition_arns[spawner.get_env()["JUPYTERHUB_USER"]],
    'overrides': {
        'taskRoleArn': os.environ.get('FARGATE_SPAWNER_TASK_ROLE_ARN'),
        'containerOverrides': [{
            'command': [
                '/opt/conda/bin/jupyterhub-singleuser',
                '--config=jupyter_server_config.py'
            ],
            'environment': [
                {
                    'name': name,
                    'value': value,
                } for name, value in
                ([n, v] for [n, v] in spawner.get_env().items() if n != 'PATH')
            ],
            'name': os.environ.get('FARGATE_SPAWNER_CONTAINER_NAME')
        }],
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

# Cull single-user processes that are idle (1800 seconds = half hour)
c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'command': [
            sys.executable, '-m',
            'jupyterhub_idle_culler', '--timeout=1800'
        ],
    }
]

c.JupyterHub.load_roles = [
    {
        "name": "list-and-cull",  # name the role
        "services": [
            "idle-culler",  # assign the service to this role
        ],
        "scopes": [
            # declare what permissions the service should have
            "list:users",  # list users
            "read:users:activity",  # read user last-activity
            "admin:servers",  # start/stop servers
        ],
    }
]
