import ipaddress
from aws_cdk import (core, aws_ec2)


class SubnetGroup:
    def __init__(self, scope: core.Construct, vpc: aws_ec2.CfnVPC,
                 **kwargs) -> None:

        self._cidr_mask = scope.node.try_get_context("subnet_cidr_cidr")
        self._desired_azs = len(scope.node.try_get_context("azs"))
        self._desired_layers = len(scope.node.try_get_context("azs"))
        self._private_enabled = True
        self._region = scope.node.try_get_context("region")
        self._azs = scope.node.try_get_context("azs")
        self._reserved_azs = 4
        self._reserved_layers = 4
        self._scope = scope
        self._vpc = vpc

        self._desired_subnet_points = []
        for layer_number in range(self._desired_layers):
            for az_number in range(self._desired_azs):
                self._desired_subnet_points.append([layer_number, az_number])

        self._public_subnets = []
        self._private_subnets = []

    @property
    def cidr_mask(self) -> int:
        return self._cidr_mask

    @property
    def desired_azs(self) -> int:
        return self._desired_azs

    @property
    def desired_layers(self) -> int:
        return self._desired_layers

    @property
    def desired_subnet_points(self) -> list:
        return self._desired_subnet_points

    @property
    def private_enabled(self) -> bool:
        return self._private_enabled

    @property
    def private_subnets(self) -> list:
        return self._private_subnets

    @property
    def public_subnets(self) -> list:
        return self._public_subnets

    @property
    def region(self) -> str:
        return self._region

    @property
    def reserved_azs(self) -> int:
        return self._reserved_azs

    @property
    def reserved_layers(self) -> int:
        return self._reserved_layers

    @property
    def scope(self) -> core.Construct:
        return self._scope

    @property
    def vpc(self) -> aws_ec2.CfnVPC:
        return self._vpc

    def create_subnets(self) -> None:
        netwk = ipaddress.ip_network(self.vpc.cidr_block)
        cidrs = list(netwk.subnets(new_prefix=self.cidr_mask))
        cidrs.reverse()
        az_name = self._azs
        vpc_id = [
            tag['value'] for tag in self.vpc.tags.render_tags()
            if tag['key'] == 'Name'
        ].pop()

        for layer in range(self.reserved_layers):
            for az_number in range(self.reserved_azs):
                current = [layer, az_number]
                cidr = str(cidrs.pop())
                if current in self.desired_subnet_points:
                    az_end = az_name[az_number][-2:]
                    subnet_type = "private" if self.private_enabled and layer > 0 else "public"

                    subnet = aws_ec2.CfnSubnet(
                        self.scope,
                        f'{vpc_id}-{subnet_type}-{az_end}',
                        cidr_block=cidr,
                        vpc_id=self.vpc.ref,
                        availability_zone=az_name[az_number],
                        tags=[
                            core.CfnTag(
                                key='Name',
                                value=f'{vpc_id}-{subnet_type}-{az_end}',
                            ),
                            core.CfnTag(
                                key='Layer',
                                value=f'{layer}',
                            ),
                            core.CfnTag(
                                key='AZNumber',
                                value=f'{az_number}',
                            ),
                        ],
                    )
                    if self.private_enabled and layer > 0:
                        self._private_subnets.append(subnet)
                    else:
                        self._public_subnets.append(subnet)
