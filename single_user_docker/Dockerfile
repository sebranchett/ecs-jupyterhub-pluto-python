FROM jupyter/minimal-notebook:latest

USER root
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.7/julia-1.7.3-linux-x86_64.tar.gz && \
    tar -xvzf julia-1.7.3-linux-x86_64.tar.gz && \
    mv julia-1.7.3 /opt/ && \
    ln -s /opt/julia-1.7.3/bin/julia /usr/local/bin/julia && \
    rm julia-1.7.3-linux-x86_64.tar.gz

USER ${NB_USER}

RUN julia -e "import Pkg; Pkg.add([\"PlutoUI\", \"Pluto\"]); Pkg.precompile()"

RUN pip3 install jupyter-server-proxy && \
    pip3 install git+https://github.com/sebranchett/pluto-on-jupyterlab.git

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache -r /tmp/requirements.txt

RUN mkdir -p ~/.jupyter
COPY jupyter_server_config.py ~/.jupyter/jupyter_server_config.py
RUN bash -c 'echo hello btsa'
RUN bash -c 'echo $PATH'
RUN bash -c 'which jupyterhub-singleuser'
