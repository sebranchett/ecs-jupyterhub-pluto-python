#!/usr/bin/env python3
import yaml

from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elb,
    aws_route53 as route53,
    aws_route53_targets as route53_targets,
    aws_certificatemanager as acm,
    App, CfnOutput, Stack
)


class LoadBalancerStack(Stack):
    def __init__(self, app: App, id: str) -> None:
        super().__init__(app, id)

        # General configuration variables
        config_yaml = yaml.load(
            open('config.yaml'), Loader=yaml.FullLoader)
        base_name = config_yaml["base_name"]
        domain_prefix = config_yaml['domain_prefix']
        application_prefix = 'pluto-' + domain_prefix
        hosted_zone_id = config_yaml['hosted_zone_id']
        hosted_zone_name = config_yaml['hosted_zone_name']
        certificate_arn = config_yaml['certificate_arn']

        vpc = ec2.Vpc(self, "VPC")

        data = open("./httpd.sh", "rb").read()
        httpd = ec2.UserData.for_linux()
        httpd.add_commands(str(data, 'utf-8'))

        asg = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            user_data=httpd,
        )

        load_balancer = elb.ApplicationLoadBalancer(
            self, f'{base_name}LoadBalancer',
            vpc=vpc,
            internet_facing=True)

        hosted_zone = \
            route53.PublicHostedZone.from_hosted_zone_attributes(
                self,
                f'{base_name}HostedZone',
                hosted_zone_id=hosted_zone_id,
                zone_name=hosted_zone_name
            )

        route53_record = route53.ARecord(
            self,
            f'{base_name}ELBRecord',
            zone=hosted_zone,
            record_name=application_prefix,
            target=route53.RecordTarget(alias_target=(
                route53_targets.LoadBalancerTarget(
                    load_balancer=load_balancer)))
        )

        """
        certificate = acm.Certificate(
            self,
            f'{base_name}Certificate',
            domain_name='*.' + hosted_zone.zone_name,
            validation=acm.CertificateValidation.from_dns(
                hosted_zone=hosted_zone)
        )
        # SEB validation can take from 30 minutes to hours, timeout 72 hours
        # Need to find a better way to split this out
        """

        certificate = acm.Certificate.from_certificate_arn(
            self, "Certificate", certificate_arn
        )
        listener = load_balancer.add_listener(
            f'{base_name}ServiceELBListener',
            port=443,
            protocol=elb.ApplicationProtocol.HTTPS,
            certificates=[certificate]
        )

        listener.add_targets(
            "Target", port=443,
            targets=[asg]
        )

        asg.scale_on_request_count(
            "AModestLoad", target_requests_per_minute=60
        )

        # Output the service URL to CloudFormation outputs
        CfnOutput(
            self,
            f'{base_name}HubURL',
            value='https://' + route53_record.domain_name
        )


app = App()
LoadBalancerStack(app, "LoadBalancerStack")
app.synth()
