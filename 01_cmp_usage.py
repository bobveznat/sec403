"""Uses AssumeRole to gain access to a customer account.

Assumes the role created in the customer account by 01_customer_setup.py.
"""
import boto.sts
import boto.ec2


customer_id = '540535557624'
role_name = 'easy-describe'

sts_conn = boto.sts.STSConnection()

# Get AWS to give us a set of temporary credentials that act inside of
# `customer_id`'s account.
role_arn = 'arn:aws:iam::%s:role/%s' % (customer_id, role_name,)
assumed_role = sts_conn.assume_role(role_arn, 'TheRoleSessionName')

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

print 'credentials.access_key:', assumed_role.credentials.access_key
print 'credentials.expiration:', assumed_role.credentials.expiration

print 'user.arn:', assumed_role.user.arn
print 'user.assume_role_id:', assumed_role.user.assume_role_id
