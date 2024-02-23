from aws_cdk import (aws_iam as iam, aws_ec2 as ec2, core)


class SecurityStack(core.Stack):
    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc: ec2.Vpc,
                 stage={},
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prefix_name = f'{stage["vpc_prefix"]}-{stage["stage_name"]}-{self.node.try_get_context("customer")}'

        bastion_sg = ec2.SecurityGroup(
            self,
            f'{prefix_name}-public-bastion-sg',
            security_group_name=f'{prefix_name}-public-bastion-sg-group',
            vpc=vpc,
            description="SG for Bastion Host",
            allow_all_outbound=True)
        bastion_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22),
                                    "SSH Access")
        core.Tags.of(bastion_sg.node.default_child).add(
            "Name", f'{prefix_name}-public-bastion-sg')

        self._bastion_sg = bastion_sg

        alb_sg = ec2.SecurityGroup(
            self,
            f'{prefix_name}-public-alb-sg',
            security_group_name=f'{prefix_name}-public-alb-sg-group',
            vpc=vpc,
            description="SG for alb",
            allow_all_outbound=True)
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80),
                                "web traffic")
        alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443),
                                "web traffic")

        core.Tags.of(alb_sg.node.default_child).add(
            "Name", f'{prefix_name}-public-alb-sg')

        self._alb_sg = alb_sg

    @property
    def bastion_sg(self) -> ec2.ISecurityGroup:
        return self._bastion_sg

    @property
    def alb_sg(self) -> ec2.ISecurityGroup:
        return self._alb_sg
