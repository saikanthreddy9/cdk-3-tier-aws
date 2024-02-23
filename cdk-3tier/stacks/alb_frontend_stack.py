from aws_cdk import (aws_ec2 as ec2, aws_iam as iam, core,
                     aws_elasticloadbalancingv2 as elb, aws_autoscaling as
                     autoscaling)

with open("stacks/scripts/install_httpd.sh") as f:
    user_data = f.read()


class AlbFrontendStack(core.Stack):
    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc: ec2.Vpc,
                 sg: ec2.ISecurityGroup,
                 stage={},
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prefix_name = f'{stage["vpc_prefix"]}-{stage["stage_name"]}-{self.node.try_get_context("customer")}'
        linux_ami = ec2.AmazonLinuxImage(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE)

        alb = elb.ApplicationLoadBalancer(
            self,
            f'{prefix_name}-public-alb',
            vpc=vpc,
            security_group=sg,
            internet_facing=True,
            load_balancer_name=f'{prefix_name}-public-alb')

        target_group = elb.ApplicationTargetGroup(
            self,
            f'{prefix_name}-public-alb-tg',
            port=80,
            vpc=vpc,
            target_type=elb.TargetType.INSTANCE,
            target_group_name=f'{prefix_name}-public-alb-tg',
            stickiness_cookie_duration=core.Duration.days(1))

        alb.add_listener(f'{prefix_name}-public-alb-listener',
                         port=80,
                         open=True,
                         default_target_groups=[target_group])

        web_server_role = iam.Role(
            self,
            f'{prefix_name}-public-role',
            assumed_by=iam.ServicePrincipal('ec2.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'AmazonS3ReadOnlyAccess')
            ])

        asg_update_policy = autoscaling.UpdatePolicy.rolling_update(
            min_instances_in_service=1, pause_time=core.Duration.minutes(2))

        self.asg = autoscaling.AutoScalingGroup(
            self,
            f'{prefix_name}-asg',
            auto_scaling_group_name=f'{prefix_name}-asg',
            instance_type=ec2.InstanceType(
                instance_type_identifier=stage['private_instance_type']),
            machine_image=linux_ami,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE),
            role=web_server_role,
            cooldown=core.Duration.seconds(300),
            key_name=stage["key_name"],
            desired_capacity=stage["desired_capacity"],
            min_capacity=stage["min_capacity"],
            max_capacity=stage["max_capacity"],
            user_data=ec2.UserData.custom(user_data),
            update_policy=asg_update_policy)

        core.Tags.of(self.asg).add("Name", f'{prefix_name}-asg-instance')

        self.asg.connections.allow_from(
            alb,
            ec2.Port.tcp(80),
            description="Allows ASG Security Group receive traffic from ALB")
        self.asg.connections.allow_from(
            alb,
            ec2.Port.tcp(443),
            description="Allows ASG Security Group receive traffic from ALB")

        self.asg.attach_to_application_target_group(target_group)

        self.asg.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            cooldown=core.Duration.seconds(60),
        )

        self._asg_sg = self.asg.connections.security_groups

        core.CfnOutput(self,
                       "alb_url",
                       value=f"http://{alb.load_balancer_dns_name}",
                       description="Web Server ALB Domain Name")

    @property
    def asg_sg(self) -> ec2.ISecurityGroup:
        return self._asg_sg
