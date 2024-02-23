from aws_cdk import (aws_ec2 as ec2, aws_iam as iam, core)


class BastionStack(core.Stack):
    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc: ec2.Vpc,
                 sg: ec2.ISecurityGroup,
                 stage={},
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prefix_name = f'{stage["vpc_prefix"]}-{stage["stage_name"]}-{self.node.try_get_context("customer")}'

        cfn_key_pair = ec2.CfnKeyPair(self, "MyCfnKeyPair",
            key_name=stage["key_name"],
        )
        bastion_host = ec2.Instance(
            self,
            f'{prefix_name}-public-bastion',
            instance_type=ec2.InstanceType('t3.micro'),
            machine_image=ec2.AmazonLinuxImage(
                edition=ec2.AmazonLinuxEdition.STANDARD,
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                virtualization=ec2.AmazonLinuxVirt.HVM,
                storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE),
            vpc=vpc,
            key_name=stage["key_name"],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg)

        core.Tags.of(bastion_host).add("Name", f'{prefix_name}-public-bastion')

        core.CfnOutput(self, 'my-bastion-id', value=bastion_host.instance_id)
