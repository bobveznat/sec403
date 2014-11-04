import boto.sts
import boto.ec2

import iam_utils


customer_id = '540535557624'
role_name = 'easy-describe'

sts_conn = boto.sts.STSConnection()

# Get AWS to give us a set of temporary credentials that act inside of
# `customer_id`'s account.
role_arn = 'arn:aws:iam::%s:role/%s' % (customer_id, role_name,)
print role_arn
assumed_role = sts_conn.assume_role(role_arn, 'sec-403-demo')
token = iam_utils.Token(assumed_role.credentials)

# Using the temporary creds, run DescribeInstances
ec2_conn = boto.ec2.connect_to_region('us-west-2', **token.to_boto_dict())
ec2_conn.get_all_instances()
