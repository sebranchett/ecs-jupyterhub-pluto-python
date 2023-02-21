# Configuration file for jupyter-server.
from jupyter_client.localinterfaces import public_ips

c = get_config()
# Where am I?
# this from: https://github.com/jupyterhub/dockerspawner/issues/198
# "nils-werner commented on Jul 12, 2018"
ip = public_ips()[0]

# The IP address the Jupyter server will listen on.
c.ServerApp.ip = ip

# The port the server will listen on (env: JUPYTER_PORT).
c.ServerApp.port = 8888

# Allow requests where the Host header doesn't point to a local server
c.ServerApp.allow_remote_access = True
