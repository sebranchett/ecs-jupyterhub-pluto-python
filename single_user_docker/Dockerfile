# make sure the single user version is compatile with the hub version
FROM jupyter/minimal-notebook:hub-3.1.1

# check there is a jupyter process running
HEALTHCHECK CMD pgrep "jupyter" > /dev/null || exit 1

USER root
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.8/julia-1.8.5-linux-x86_64.tar.gz && \
    tar -xvzf julia-1.8.5-linux-x86_64.tar.gz && \
    mv julia-1.8.5 /opt/ && \
    ln -s /opt/julia-1.8.5/bin/julia /usr/local/bin/julia && \
    rm julia-1.8.5-linux-x86_64.tar.gz

RUN chown -R jovyan:users /home/jovyan && chmod -R 755 /home/jovyan

USER ${NB_USER}

RUN julia -e "import Pkg; Pkg.add([\"PlutoUI\", \"Pluto\"]); Pkg.precompile()"

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt

RUN mkdir -p .jupyter
COPY jupyter_server_config.py .jupyter/jupyter_server_config.py

# Create a shared read only reference directory
# The read-only restriction is applied by the AWS mount
RUN mkdir -p /home/jovyan/reference

WORKDIR /home/jovyan/work
