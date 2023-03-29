FROM jupyterhub/jupyterhub:3.1.1

LABEL Project Jupyter <ipython-dev@scipy.org>

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt

# Create oauthenticator directory and put necessary files in it
RUN mkdir /srv/oauthenticator
WORKDIR /srv/oauthenticator
ENV OAUTHENTICATOR_DIR /srv/oauthenticator
COPY jupyterhub_config.py jupyterhub_config.py
RUN chmod 700 /srv/oauthenticator

EXPOSE 8000
CMD ["jupyterhub"]

USER ${NB_USER}
