from aws_cdk import (
    core,
    aws_ec2,
)


def create_privagte_route_table(
        scope: core.Construct, vpc: aws_ec2.CfnVPC,
        nat_gateway: aws_ec2.CfnNatGateway) -> aws_ec2.CfnRouteTable:

    prefix = scope.node.try_get_context("prefix")
    az_name = [
        tag['value'] for tag in nat_gateway.tags.render_tags()
        if tag['key'] == 'Name'
    ].pop()
    az_end = az_name[-2:]
    route_table = aws_ec2.CfnRouteTable(
        scope,
        f'{prefix}-route-table-nat-{az_end}',
        vpc_id=vpc.ref,
        tags=[core.CfnTag(
            key='Name',
            value=f'{prefix}-route-table-nat',
        )],
    )

    aws_ec2.CfnRoute(
        scope,
        f'{prefix}-route-nat-{az_end}',
        route_table_id=route_table.ref,
        destination_cidr_block='0.0.0.0/0',
        nat_gateway_id=nat_gateway.ref,
    )
    return route_table


def create_public_route_table(
        scope: core.Construct, vpc: aws_ec2.CfnVPC,
        internet_gateway: aws_ec2.CfnInternetGateway) -> aws_ec2.CfnRouteTable:

    prefix = scope.node.try_get_context("prefix")
    route_table = aws_ec2.CfnRouteTable(
        scope,
        f'{prefix}-route-table-igw',
        vpc_id=vpc.ref,
        tags=[core.CfnTag(
            key='Name',
            value=f'{prefix}-route-table-igw',
        )],
    )

    aws_ec2.CfnRoute(
        scope,
        f'{prefix}-route-igw',
        route_table_id=route_table.ref,
        destination_cidr_block='0.0.0.0/0',
        gateway_id=internet_gateway.ref,
    )
    return route_table


def create_route_table_association(
    scope: core.Construct, vpc: aws_ec2.CfnVPC, subnet: aws_ec2.CfnSubnet,
    route_table: aws_ec2.CfnRouteTable
) -> aws_ec2.CfnSubnetRouteTableAssociation:

    prefix = scope.node.try_get_context("prefix")
    route_table_type = [
        tag['value'] for tag in route_table.tags.render_tags()
        if tag['key'] == 'Name'
    ].pop()
    az_end = subnet.availability_zone[-2:]

    association = aws_ec2.CfnSubnetRouteTableAssociation(
        scope,
        f'{prefix}-subnet-route-table-association-{route_table_type[-3:]}-{az_end}',
        route_table_id=route_table.ref,
        subnet_id=subnet.ref,
    )
    return association
