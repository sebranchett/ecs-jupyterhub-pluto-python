# Configuration file for jupyter-server.
from jupyter_client.localinterfaces import public_ips

c = get_config()
# Where am I?
# this from: https://github.com/jupyterhub/dockerspawner/issues/198
# "nils-werner commented on Jul 12, 2018"
ip = public_ips()[0]

# The IP address the Jupyter server will listen on.
#  Default: 'localhost'
c.ServerApp.ip = ip

# The port the server will listen on (env: JUPYTER_PORT).
#  Default: 0
c.ServerApp.port = 8888

# # Allow requests where the Host header doesn't point to a local server

#         By default, requests get a 403 forbidden response if the 'Host'
#         header shows that the browser thinks it's on a non-local domain.
#         Setting this option to True disables this check.
#
#         This protects against 'DNS rebinding' attacks, where a remote web
#         server serves you a page and then changes its DNS to send later
#         requests to a local IP, bypassing same-origin checks.
#
#         Local IP addresses (such as 127.0.0.1 and ::1) are allowed as local,
#         along with hostnames configured in local_hostnames.
#  Default: False
c.ServerApp.allow_remote_access = True

# # Hostnames to allow as local when allow_remote_access is False.
#
#         Local IP addresses (such as 127.0.0.1 and ::1) are automatically
#         accepted as local as well.
#  Default: ['localhost']
# c.ServerApp.local_hostnames = [ip]
