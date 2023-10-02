# Configuration file for jupyter-server.

c = get_config()

# The IP address the Jupyter server will listen on
# See https://jupyter-server.readthedocs.io/en/latest/operators/public-server.html#running-a-public-notebook-server
c.ServerApp.ip = '*'

# The port the server will listen on (env: JUPYTER_PORT)
c.ServerApp.port = 8888

# Allow requests where the Host header doesn't point to a local server
c.ServerApp.allow_remote_access = True
