# Building up slowly

Starting point is the [Application Load Balancer example](https://github.com/aws-samples/aws-cdk-examples/tree/master/python/application-load-balancer), under an [Apache 2.0 License](https://github.com/aws-samples/aws-cdk-examples/blob/master/LICENSE).

This work is heavily based on the [Jupyter ECS Service CDK project](https://github.com/avishayil/jupyter-ecs-service), under an [Apache 2.0 License](https://github.com/sebranchett/serverless-jupyter-python/blob/main/LICENSE). See also [Avishay Bar's blog post](https://avishayil.medium.com/serverless-jupyter-hub-with-aws-fargate-and-cdk-2160154187a1).

*WARNING:* Validating a certificate can take 30 minutes to hours! The validation will time out after 72 hours.