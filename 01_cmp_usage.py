import boto.sts
import boto.ec2

import iam_utils


customer_id = '540535557624'
role_name = 'easy-describe'

sts_conn = boto.sts.STSConnection()

# Get AWS to give us a set of temporary credentials that act inside of
# `customer_id`'s account.
role_arn = 'arn:aws:iam::%s:role/%s' % (customer_id, role_name,)
assumed_role = sts_conn.assume_role(role_arn, 'sec-403-demo')

# Using the temporary creds, run DescribeInstances
ec2_conn = boto.ec2.connect_to_region(
    'us-west-2',
    aws_access_key_id=assumed_role.credentials.access_key,
    aws_secret_access_key=assumed_role.credentials.secret_key,
    security_token=assumed_role.credentials.session_token,
)

# Under the hood this calls DescribeInstances
instances = ec2_conn.get_only_instances()
for instance in instances:
    print instance.id, instance.tags

import ipdb; ipdb.set_trace()

