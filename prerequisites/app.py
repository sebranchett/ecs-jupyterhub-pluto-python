#!/usr/bin/env python3
import os
import yaml

from aws_cdk import (
    aws_cognito as cognito,
    App, Environment, CfnOutput, Stack, RemovalPolicy
)


class PreReqStack(Stack):
    def __init__(self, app: App, id: str, **kwargs) -> None:
        super().__init__(app, id, **kwargs)

        # General configuration variables
        config_yaml = yaml.load(
            open('../config.yaml'), Loader=yaml.FullLoader)
        base_name = config_yaml["base_name"]

        # User pool and user pool OAuth client
        cognito_user_pool = cognito.UserPool(
            self,
            f'{base_name}UserPool',
            removal_policy=RemovalPolicy.DESTROY,
            self_sign_up_enabled=False
        )

        # Output Cognito user pool id for SAML interface
        CfnOutput(
            self,
            f'{base_name}UserPoolID',
            value=cognito_user_pool.user_pool_id
        )


default_env = Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=os.environ["CDK_DEFAULT_REGION"]
)
app = App()
PreReqStack(app, "PreReqStack", env=default_env)

app.synth()
