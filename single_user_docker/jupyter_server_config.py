# Configuration file for jupyter-server.

c = get_config()

# Set ip to '*' to bind on all interfaces (ips) for the hub server
c.ServerApp.ip = '*'

# The port the server will listen on (env: JUPYTER_PORT)
c.ServerApp.port = 8888

# Allow requests where the Host header doesn't point to a local server
c.ServerApp.allow_remote_access = True
