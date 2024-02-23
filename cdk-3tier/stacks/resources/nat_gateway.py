from aws_cdk import (core, aws_ec2)


def create_nat_gateway(scope: core.Construct, vpc: aws_ec2.CfnVPC,
                       subnet: aws_ec2.CfnSubnet) -> aws_ec2.CfnNatGateway:
    prefix = scope.node.try_get_context("prefix")
    az_end = subnet.availability_zone[-2:]
    eip = aws_ec2.CfnEIP(scope, f'{prefix}-eip-{az_end}')

    nat_gateway = aws_ec2.CfnNatGateway(
        scope,
        f'{prefix}-nat-{az_end}',
        allocation_id=eip.attr_allocation_id,
        subnet_id=subnet.ref,
        tags=[core.CfnTag(
            key='Name',
            value=f'{prefix}-nat-{az_end}',
        )],
    )
    return nat_gateway
