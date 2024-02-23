from aws_cdk import (core, aws_ec2 as _ec2)

class VpcStack(core.Stack):
    @property
    def availability_zones(self):
        return self.node.try_get_context("azs")

    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 stage={},
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        customer = self.node.try_get_context("customer")
        stage_name = stage["stage_name"]
        vpc_cidr = stage["vpc_cidr"]
        vpc_prefix = stage["vpc_prefix"]
        prefix_name = f'{vpc_prefix}-{stage_name}-{customer}'
        subnet_prefix = int(stage['subnet_prefix'])
        max_azs = int(stage['max_azs'])
        nat_number = int(stage['nat_number'])
        layers = stage['layers']
        layer_endpoints = stage['layer_endpoints']
        layers_nat = stage['layer_nats']

        flag_public = False
        flag_private = False
        flag_isolated = False

        subnets_config = []
        for layer in layers:
            layer_type = layers[layer]
            if layer_type == 'PUBLIC':
                subnet_type = _ec2.SubnetType.PUBLIC
                flag_public = True
            if layer_type == 'PRIVATE':
                subnet_type = _ec2.SubnetType.PRIVATE
                flag_private = True
            if layer_type == 'ISOLATED':
                flag_isolated = True
                subnet_type = _ec2.SubnetType.ISOLATED
            subnets_config.append(
                _ec2.SubnetConfiguration(name=layer,
                                         subnet_type=subnet_type,
                                         cidr_mask=subnet_prefix))

        nat_subnets = None
        if layers_nat in layers and layers[layers_nat] == 'PUBLIC':
            nat_subnets = _ec2.SubnetSelection(subnet_group_name=layers_nat)

        vpc_tenacy = _ec2.DefaultInstanceTenancy.DEFAULT
        if self.node.try_get_context("vpc_tenacy") == 'DEDICATED':
            vpc_tenacy = _ec2.DefaultInstanceTenancy.DEDICATED

        subnet_layer_endpoints = [
            _ec2.SubnetSelection(one_per_az=True,
                                 subnet_group_name=layer_endpoints)
        ]

        self.vpc = _ec2.Vpc(
            self,
            prefix_name,
            max_azs=max_azs,
            cidr=vpc_cidr,
            subnet_configuration=subnets_config,
            nat_gateway_subnets=nat_subnets,
            nat_gateways=nat_number,
            default_instance_tenancy=vpc_tenacy,
            gateway_endpoints={
                "S3":
                _ec2.GatewayVpcEndpointOptions(
                    service=_ec2.GatewayVpcEndpointAwsService.S3,
                    subnets=subnet_layer_endpoints)
            })

        # tagging
        core.Tags.of(self.vpc.node.default_child).add("Name",
                                                      f'{prefix_name}-vpc')
        core.Tags.of(self.vpc.node.find_child('IGW')).add(
            "Name", f'{prefix_name}-igw')

        prisub = [prs for prs in self.vpc.private_subnets]
        pubsub = [pus for pus in self.vpc.public_subnets]
        isosub = [ios for ios in self.vpc.isolated_subnets]

        count = 1
        for nat in stage['nat_number']:
            core.Tags.of(
                self.vpc.node.find_child('publicSubnet' + str(count)).node.
                find_child('NATGateway')).add("Name", f'{prefix_name}-nat')
            core.Tags.of(
                self.vpc.node.find_child(
                    'publicSubnet' + str(count)).node.find_child("EIP")).add(
                        "Name", f'{prefix_name}-public-eip-{count}')
            count += 1

        count = 1
        for prs in prisub:
            az_end = prs.availability_zone[-2:]
            core.Tags.of(prs.node.default_child).add(
                "Name", f'{prefix_name}-private-{az_end}')
            core.Tags.of(
                self.vpc.node.find_child(
                    'privateSubnet' +
                    str(count)).node.find_child('RouteTable')).add(
                        "Name", f'{prefix_name}-private-rt-{az_end}')
            count += 1

        count = 1
        for pus in pubsub:
            az_end = pus.availability_zone[-2:]
            core.Tags.of(pus.node.default_child).add(
                "Name", f'{prefix_name}-public-{az_end}')
            core.Tags.of(
                self.vpc.node.find_child(
                    'publicSubnet' +
                    str(count)).node.find_child('RouteTable')).add(
                        "Name", f'{prefix_name}-public-rt-{az_end}')
            count += 1

        count = 1
        for ios in isosub:
            az_end = ios.availability_zone[-2:]
            core.Tags.of(ios.node.default_child).add(
                "Name", f'{prefix_name}-database-{az_end}')
            core.Tags.of(
                self.vpc.node.find_child(
                    'databaseSubnet' +
                    str(count)).node.find_child('RouteTable')).add(
                        "Name", f'{prefix_name}-database-rt-{az_end}')
            count += 1

        core.CfnOutput(self, "Output", value=self.vpc.vpc_id)
