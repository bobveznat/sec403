"""Setup EC2 instance profiles for our cloud management platform.

In our simplified example of the world we assume a reasonably straightforward
3-tier application: A frontend web tier, an application tier, a distributed
queue and a pool of worker nodes taking items from the queue.

In the context of SEC403 we are concerned with security and getting our app and
worker tiers to act on behalf of our customer accounts in a safe and trusted
way. We always ask what is the least amount of privilege we need to do our job
and then construct appropriate policies.

Let's pretend that our little application here provides a web-based view to a
customer's AWS infrastructure and allows them to stop and start instances
running in their environment.

In this example we've decided that our app tier needs the ability to
DescribeInstances inside of customer accounts and to submit worker items into
an SQS queue named `theQueueName`. Despite it being a poor design decision
we're going to allow our app tier to talk directly to the AWS API in order to
run DescribeInstances and view the current inventory of instances running
within an account. If a request to stop or start an instance comes in to the
app tier it will be enqueued as a task on our SQS queue and effectively passed
down to the worker tier.

Our worker tier needs to be able to pull items off of the queue and work on
them and in addition it may need to call Start or StopInstances inside of a
customer account.
"""
import boto.iam

from awacs.aws import Allow, Policy, Statement, Principal
from awacs import ec2, iam, sts, sqs

import iam_utils


iam_conn = boto.iam.connect_to_region('universal')

my_aws_account_id = '032298565451'

# Here, and we do this again in modifyinstances_role_arn below, we have a
# placed an asterisk in the account id section of the arn. This allows the user
# of this policy to assume a role named ReadonlyPolicy within any
# customer account that allows us to (via their trust policy)
readonly_role_arn = 'arn:aws:iam::*:role/ReadonlyPolicy'
modifyinstances_role_arn = 'arn:aws:iam::*:role/ModifyInstancesPolicy'

cloudwatch_role_arn = iam.ARN('*', 'role/brkt-cloudwatch')
sqs_arn = sqs.ARN('us-west-2', my_aws_account_id, 'theQueueName')

worker_access_policy = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[
                sqs.ChangeMessageVisibility,
                sqs.DeleteMessage,
                sqs.GetQueueAttributes,
                sqs.GetQueueUrl,
                sqs.ReceiveMessage,
            ],
            Resource=[sqs_arn],
        ),
        Statement(
            Effect=Allow,
            Action=[sts.AssumeRole],
            Resource=[modifyinstances_role_arn],
        ),
    ]
)

apptier_access_policy = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[
                sqs.ChangeMessageVisibility,
                sqs.DeleteMessage,
                sqs.GetQueueAttributes,
                sqs.GetQueueUrl,
                sqs.SendMessage,
            ],
            Resource=[sqs_arn],
        ),
        Statement(
            Effect=Allow,
            Action=[sqs.CreateQueue],
            Resource=['*'],
        ),
        Statement(
            Effect=Allow,
            Action=[sts.AssumeRole],
            Resource=[readonly_role_arn],
        ),
    ]
)

instance_profile_trust = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[sts.AssumeRole],
            Principal=Principal('Service', 'ec2.amazonaws.com'),
        )
    ]
)

iam_utils.update_policy(
    iam_conn,
    'worker',
    'worker-access-policy',
    instance_profile_trust.to_json(),
    worker_access_policy.to_json(),
    profile=True,
)

iam_utils.update_policy(
    iam_conn,
    'apptier',
    'apptier-access-policy',
    instance_profile_trust.to_json(),
    apptier_access_policy.to_json(),
    profile=True,
)
