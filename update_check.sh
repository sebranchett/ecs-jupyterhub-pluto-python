#!/bin/bash

JUPYTERHUB_CURRENT="$(grep 'FROM ' hub_docker/Dockerfile | sed 's/^.*://g')"
JUPYTERHUB_LATEST="$(curl -s https://hub.docker.com/v2/repositories/jupyterhub/jupyterhub/tags?page_size=50 |jq -r '.results[] .name '|sort -V |grep -E '^[0-9]+[.][0-9]+[.][0-9]+$'|tail -1)"

echo -e "Jupyterhub:\tlatest\t$JUPYTERHUB_LATEST \tcurrent\t$JUPYTERHUB_CURRENT"

SINGLE_USER="$(grep 'FROM ' single_user_docker/Dockerfile | sed 's/^.* jupyter\///g')"

echo -e "Single user base image:\t\tcurrent\t$SINGLE_USER"

JULIA_LATEST="$(curl -s https://api.github.com/repos/JuliaLang/julia/releases/latest|jq -r .tag_name |sed 's/[^0-9\.]//g' )"
JULIA_CURRENT="$(grep -E '^ENV JULIA_VERSION=' single_user_docker/Dockerfile  |sed 's/^.*=//g' )"

echo -e "Julia:\t\tlatest\t$JULIA_LATEST \tcurrent\t$JULIA_CURRENT"
