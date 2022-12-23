# Building up slowly

This repository is intended for researchers who wish to provide their group with a Jupyter or Pluto environment. The environment provides access to group specific tools and shared, read-only data. This data would typically be images used for testing algorithms, raw experimental data, course material for advanced students, etc.

Starting points are: 
* the [Application Load Balancer example](https://github.com/aws-samples/aws-cdk-examples/tree/master/python/application-load-balancer), under an [Apache 2.0 License](https://github.com/aws-samples/aws-cdk-examples/blob/master/LICENSE)
* the [Fargate Load Balanced Service example](https://github.com/aws-samples/aws-cdk-examples/tree/master/python/ecs/fargate-load-balanced-service), under an [Apache 2.0 License](https://github.com/aws-samples/aws-cdk-examples/blob/master/LICENSE)

This work is heavily based on the [Jupyter ECS Service CDK project](https://github.com/avishayil/jupyter-ecs-service), under an [Apache 2.0 License](https://github.com/sebranchett/serverless-jupyter-python/blob/main/LICENSE). See also [Avishay Bar's blog post](https://avishayil.medium.com/serverless-jupyter-hub-with-aws-fargate-and-cdk-2160154187a1).

The adaptation for Pluto is inspired by [plutohub-juliacon2021](https://github.com/barche/plutohub-juliacon2021) (no license supplied) and [pluto-on-jupyterlab](https://github.com/pankgeorg/pluto-on-jupyterlab), under an [Unlicense license](https://github.com/pankgeorg/pluto-on-jupyterlab/blob/master/LICENSE) and adapts this [Pluto server](https://github.com/fonsp/pluto-on-jupyterlab), under an [Unlicense license](https://github.com/fonsp/pluto-on-jupyterlab/blob/master/LICENSE).

The adaptations and original work in this repository are provided under an [Apache 2.0 License](LICENSE).

## Architecture

This architecture uses serverless services in order to remove the need from managing servers. EFS is used as shared, persistent storage for storing data and the Jupyter and Pluto notebooks.

![Jupyter on ECS Architecture](architecture_diagram/serverless_pluto_hub.png "Jupyter on ECS Architecture")

## Pre-requisites

- An AWS account with aws-cdk set up on your local machine. See [Setting up the environment](https://github.com/sebranchett/ec2-instance-python#setting-up-the-environment)
- Python 3.6 or later with requirements installed. See [Using this example](https://github.com/sebranchett/ec2-instance-python#using-this-example)
- Domain name managed with a public hosted zone on AWS Route 53.
  Please collect this information and fill the `config.yaml` file with the hosted zone name and hosted zone id from Route 53.
- [AWS managed certificate](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html), [DNS validated](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html) for your domain name.
  Please collect the ARN of your certificate and add it to the `config.yaml` file.
  
  *WARNING:* Validating a certificate can take 30 minutes to hours! Validation will time out after 72 hours.
  
  If it takes longer than 30 minutes, make sure that your Registered domain's 'Name servers' are those named in the Hosted Zone's 'NS' record. [See here](https://stackoverflow.com/a/68703299/13237339).
- A cognito user pool. If you do not yet have a suitable user pool, you can use the separate stack in the `prerequisites` folder to create one. Please collect the UserPool ID and add it to the `config.yaml` file.
- A private repository on Amazon Elastic Container Registry (ECR), in the same region you want your infrastructure. This repository should contain a JupyterHub image. See the README file in hub_docker directory.

  You can find the ARN of your image repository using the command line:
  ```
  aws ecr describe-repositories
  ```
  Please add this ARN and the image tag to the `config.yaml` file.
- A private repository on Amazon Elastic Container Registry (ECR), in the same region you want your infrastructure. This repository should contain a singe user JupyterLab image, optionally with Pluto extension. See the README file in single_use_docker directory.

  Please add this ARN and the image tag to the `config.yaml` file.

## Users
The CDK HubStack stack will provision the jupyter administrator user(s) according to the list provided in the hub_docker/admins file. A list of allowed (non-admin) users can be specified in a hub_docker/allowed_users file, see example file provided.

If you wish to add or remove users, edit the allowed_users file. You will then need to destroy the HubStack, empty the Cognito user pool and redeploy the HubStack.

If you destroy the HubStack, the Cognito users will not be deleted. You need to delete them by hand, otherwise redeploying the HubStack will fail with a message that the user already exists. This is the purpose of the `cleanup_user_pool.sh` script, which works only if you have exactly one Cognito user pool.

If you want to change the status of a user, from standard to administrator or from administrator to standard, do this in JupyterHub.

## Security

Inherited from Avishay Bar.
- You should configure the admin user temporary password on the `config.yaml` file.
- Authentication to the Jupyter hub is done by AWS Cognito user pool. When a user is logging in to the system, a user directory is automatically created for them.
- Jupyter `Shutdown on logout` is activated, To make sure that ghost processes are closed.
- ECS containers are running in non-privileged mode, according to the docker best practices.
- During the deployment time, the cdk stack will try to determine your public ip address automatically using `checkip.amazonaws.com`.
  Then, it would add only this ip address to the ingress rules of the security group of the public load balancer.
- TLS termination are being done on the application load balancer using a SSL certificate generated on the deployment time by CDK, with DNS record validation on the configured hosted zone.
- Elastic File System is encrypted with a CMK generated by AWS KMS. Key policy is restricted to the account identities.
- Permanent resources, such as EFS, CMK, and Cognito User Pool (temporarily disabled) are defined to be destroyed when the stack is deleted.

## ToDo
- Get Fargate Spawner working
- Connect non-volatile storage
- Make tests
- Rethink (bootstrap) stack organisation
