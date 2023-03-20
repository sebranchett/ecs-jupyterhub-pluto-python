FROM jupyterhub/jupyterhub:3.1.1

LABEL Project Jupyter <ipython-dev@scipy.org>

# Install oauthenticator from git
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install oauthenticator notebook
RUN python3 -m pip install fargatespawner jupyter_client jupyterhub-idle-culler

# Create oauthenticator directory and put necessary files in it
RUN mkdir /srv/oauthenticator
WORKDIR /srv/oauthenticator
ENV OAUTHENTICATOR_DIR /srv/oauthenticator
ADD jupyterhub_config.py jupyterhub_config.py
RUN chmod 700 /srv/oauthenticator

EXPOSE 8000
CMD ["jupyterhub"]
