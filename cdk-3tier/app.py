#!/usr/bin/env python3
from aws_cdk import core
from stacks.vpc_stack import VpcStack
from stacks.bastion_stack import BastionStack
from stacks.security_stack import SecurityStack
from stacks.alb_frontend_stack import AlbFrontendStack
from stacks.alb_backend_stack import AlbBackendStack 
from stacks.rds_stack import RdsStack

app = core.App()

dev_stage = app.node.try_get_context("dev")

vpc_stack = VpcStack(app,
                     "vpc",
                     env=core.Environment(account=dev_stage['account_id'],
                                          region="us-east-1"),
                     stage=dev_stage)
security_stack = SecurityStack(app,
                               "sg",
                               env=core.Environment(
                                   account=dev_stage['account_id'],
                                   region="us-east-1"),
                               vpc=vpc_stack.vpc,
                               stage=dev_stage)
bastion_stack = BastionStack(app,
                             "bastion",
                             env=core.Environment(
                                 account=dev_stage['account_id'],
                                 region="us-east-1"),
                             vpc=vpc_stack.vpc,
                             sg=security_stack.bastion_sg,
                             stage=dev_stage)
frontend_stack = AlbFrontendStack(app,
                     "frontend",
                     env=core.Environment(account=dev_stage['account_id'],
                                          region="us-east-1"),
                     vpc=vpc_stack.vpc,
                     sg=security_stack.alb_sg,
                     stage=dev_stage)
backend_stack = AlbBackendStack(app,
                     "backend",
                     env=core.Environment(account=dev_stage['account_id'],
                                          region="us-east-1"),
                     vpc=vpc_stack.vpc,
                     sg=security_stack.alb_sg,
                     stage=dev_stage)
rds_stack = RdsStack(app,
                     "rds",
                     env=core.Environment(account=dev_stage['account_id'],
                                          region="us-east-1"),
                     vpc=vpc_stack.vpc,
                     asg_sg=backend_stack.asg_sg,
                     stage=dev_stage)

app.synth()
