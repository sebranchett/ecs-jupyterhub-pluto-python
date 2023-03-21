#!/usr/bin/env python
# coding: utf-8

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.enduser import DesktopAndAppStreaming as laptop
from diagrams.aws.network import Route53
from diagrams.aws.security import Cognito
from diagrams.aws.network import ElbApplicationLoadBalancer as alb
from diagrams.aws.compute import ElasticContainerService as ecs
from diagrams.aws.storage import ElasticFileSystemEFS as efs
from diagrams.aws.compute import EC2ContainerRegistry as ecr
from diagrams.aws.compute import EC2ContainerRegistryImage as docker
from diagrams.aws.compute import Fargate
from diagrams.aws.network import VPC as vpc
from diagrams.aws.network import PublicSubnet as public
from diagrams.aws.network import PrivateSubnet as private


with Diagram(
    "\nServerless Pluto Hub", show=False, graph_attr={"fontsize": "40"}
) as serverless_pluto_hub:
    end_user = laptop("Client")
    router = Route53(label="Route 53")
    repo = ecr("Elastic Container\nRegistry")

    with Cluster("VPC"):
        with Cluster("Public Subnet over 2 AZs"):
            load_balancer = alb("Application Load\nBalancer")
            pub_subnet = public("", height="0.5")
        with Cluster("Private Subnet over 2 AZs"):
            container_service = ecs("Elastic Cloud\nService")
            docker_pluto = docker("Image for\nPluto")
            container_service - Fargate("Fargate tasks") - docker_pluto
            docker_hub = docker("Imagefor\nJupyterHub")
            container_service - Fargate("Fargate task") - docker_hub
            priv_subnet = private("", height="0.5")
        vpc = vpc("", height="0.5")
        vpc - Edge(style="invis") - pub_subnet - Edge(
            style="invis") - priv_subnet

    end_user - router
    end_user - Cognito("Cognito\nUser Pool")
    router - load_balancer - container_service - efs(
        "Elastic File\nSystem for\nPluto Notebooks"
    )
    docker_hub - repo
    docker_pluto - repo

serverless_pluto_hub
