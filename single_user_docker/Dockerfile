# should make sure the single user version is compatile with the hub version
FROM jupyter/minimal-notebook:hub-4.0.2

# check there is a jupyter process running
HEALTHCHECK CMD pgrep "jupyter" > /dev/null || exit 1

USER root
# Set up Julia
ENV JULIA_VERSION=1.9.3
ENV JULIA_MINOR=1.9
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/${JULIA_MINOR}/julia-${JULIA_VERSION}-linux-x86_64.tar.gz && \
    tar -xvzf julia-${JULIA_VERSION}-linux-x86_64.tar.gz && \
    mv julia-${JULIA_VERSION} /opt/ && \
    ln -s /opt/julia-${JULIA_VERSION}/bin/julia /usr/local/bin/julia && \
    rm julia-${JULIA_VERSION}-linux-x86_64.tar.gz

# Set up file permissions
RUN chown -R jovyan:users /home/jovyan && chmod -R 755 /home/jovyan

# Set up AWS cli
RUN wget https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip && \
    unzip awscli-exe-linux-x86_64.zip && \
    ./aws/install && \
    rm awscli-exe-linux-x86_64.zip

USER ${NB_USER}

# Precompile Pluto
RUN julia -e "import Pkg; Pkg.add([\"PlutoUI\", \"Pluto\"]); Pkg.precompile()"

# JupyterLab setup
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt

RUN mkdir -p .jupyter
COPY jupyter_server_config.py .jupyter/jupyter_server_config.py

# Create a shared read only reference directory
# The read-only restriction is applied by the AWS mount
RUN mkdir -p /home/jovyan/reference

WORKDIR /home/jovyan/work
