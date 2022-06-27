# Building up slowly

Starting point is the [Application Load Balancer example](https://github.com/aws-samples/aws-cdk-examples/tree/master/python/application-load-balancer), under an [Apache 2.0 License](https://github.com/aws-samples/aws-cdk-examples/blob/master/LICENSE).

This work is heavily based on the [Jupyter ECS Service CDK project](https://github.com/avishayil/jupyter-ecs-service), under an [Apache 2.0 License](https://github.com/sebranchett/serverless-jupyter-python/blob/main/LICENSE). See also [Avishay Bar's blog post](https://avishayil.medium.com/serverless-jupyter-hub-with-aws-fargate-and-cdk-2160154187a1).

### Pre-requisites

- An AWS account with aws-cdk set up on your local machine. See [Setting up the environment](https://github.com/sebranchett/ec2-instance-python#setting-up-the-environment)
- Python 3.6 or later with requirements installed. See [Using this example](https://github.com/sebranchett/ec2-instance-python#using-this-example)
- Domain name managed with a public hosted zone on AWS Route 53.
  Please collect this information and fill the `config.yaml` file with the hosted zone name and hosted zone id from Route 53.
- [AWS managed certificate](https://docs.aws.amazon.com/acm/latest/userguide/gs-acm-request-public.html), [DNS validated](https://docs.aws.amazon.com/acm/latest/userguide/dns-validation.html) for your domain name.
  Please collect the ARN of your certificate and add it to the `config.yaml` file.
  
  *WARNING:* Validating a certificate can take 30 minutes to hours! Validation will time out after 72 hours.
- A private repository on Amazon Elastic Container Registry (ECR), in the same region you want your  infrastructure
