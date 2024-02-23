from aws_cdk import (core, aws_ec2)


def create_vpc(scope: core.Construct, id: str) -> aws_ec2.CfnVPC:
    vpc = aws_ec2.CfnVPC(
        scope,
        f'{scope.node.try_get_context("prefix")}-vpc',
        cidr_block=scope.node.try_get_context("vpc_cidr"),
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags=[
            core.CfnTag(key='Name',
                        value=f'{scope.node.try_get_context("prefix")}')
        ])

    return vpc


def create_internet_gateway(scope: core.Construct,
                            vpc: aws_ec2.CfnVPC) -> aws_ec2.CfnInternetGateway:

    prefix = scope.node.try_get_context("prefix")
    internet_gateway = aws_ec2.CfnInternetGateway(
        scope,
        f'{prefix}-igw',
        tags=[core.CfnTag(
            key='Name',
            value=f'{prefix}-igw',
        )])

    aws_ec2.CfnVPCGatewayAttachment(
        scope,
        f'{prefix}-vpc-gateway-attachment',
        vpc_id=vpc.ref,
        internet_gateway_id=internet_gateway.ref,
    )

    return internet_gateway
