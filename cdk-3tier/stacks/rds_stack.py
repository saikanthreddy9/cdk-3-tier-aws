from aws_cdk import (aws_rds as rds, aws_ec2 as ec2, core)


class RdsStack(core.Stack):
    def __init__(self,
                 scope: core.Construct,
                 id: str,
                 vpc: ec2.Vpc,
                 asg_sg,
                 stage={},
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prefix_name = f'{stage["vpc_prefix"]}-{stage["stage_name"]}-{self.node.try_get_context("customer")}'

        self._rds_subnet_group = rds.SubnetGroup(
            self,
            f'{prefix_name}-rds-subnet-gruop',
            description="aaa",
            subnet_group_name=f'{prefix_name}-aurora-mysql',
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.ISOLATED),
            vpc=vpc)

        self._rds_cluster = rds.DatabaseCluster(
            self,
            f'{prefix_name}-rds-cluster',
            cluster_identifier=f'{prefix_name}-rds-cluster',
            credentials=rds.Credentials.from_generated_secret("testuser"),
            engine=rds.DatabaseClusterEngine.aurora_postgres(version=rds.AuroraPostgresEngineVersion.VER_11_9),
            instance_props=rds.InstanceProps(
                vpc=vpc,
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE4_GRAVITON, ec2.InstanceSize.MEDIUM),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.ISOLATED)),
            port=3306,
            default_database_name=self.node.try_get_context("customer"),
            subnet_group=self._rds_subnet_group,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(self, 'ParameterGroup', 'default.aurora-postgresql11'))
            

        for sg in asg_sg:
            self._rds_cluster.connections.allow_default_port_from(
                sg, "Allow EC2 ASG access to RDS MySQL")
