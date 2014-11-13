import boto.sts
import boto.ec2
from boto.exception import EC2ResponseError
import datetime

from awacs.aws import Allow, Policy, Statement, DateLessThan, Condition
from awacs import ec2

import iam_utils


customer_id = '540535557624'
role_name = 'easy-describe'
role_arn = 'arn:aws:iam::%s:role/%s' % (customer_id, role_name,)

sts_conn = boto.sts.STSConnection()

now_plus_60 = datetime.datetime.utcnow() + datetime.timedelta(seconds=60)
big_iso_time = now_plus_60.isoformat()
iso_time = big_iso_time[:big_iso_time.rfind('.')] + 'Z'

reduced_access_policy = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[ec2.DescribeInstances],
            Resource=['*'],
            # This reduction of policy knocks our creds down to only working
            # until iso_time. Kind of useful to work around the minimum
            # validity period of STS creds is 15 minutes.
            Condition=Condition(DateLessThan('aws:CurrentTime', iso_time)),
        ),
    ]
)


def do_tags(token):
    # Using the temporary creds, run DescribeInstances
    ec2_conn = boto.ec2.connect_to_region('us-west-2', **token.to_boto_dict())
    instances = ec2_conn.get_only_instances()
    for instance in instances:
        print instance.id, instance.tags
        try:
            ec2_conn.create_tags(instance.id, {'Key': 'Value'})
        except EC2ResponseError, e:
            if e.error_code != 'UnauthorizedOperation':
                raise
            print 'UnauthorizedOperation! Cannot set tags.'


if __name__ == '__main__':
    # Get AWS to give us a set of temporary credentials that act inside of
    # `customer_id`'s account. Here we specify our reduced access policy which
    # does not specify the CreateTags operation. This means that when we call
    # do_tags it will fail.
    assumed_role = sts_conn.assume_role(
        role_arn, 'sec-403-demo', reduced_access_policy.to_json())
    token = iam_utils.Token(assumed_role.credentials)
    print '------------ Trying with reduced privileges'
    do_tags(token)

    # Here we assume role again, this time without the reduced access policy.
    # The tagging will work
    assumed_role = sts_conn.assume_role(role_arn, 'sec-403-demo')
    token = iam_utils.Token(assumed_role.credentials)
    print '------------ Trying with full privileges'
    do_tags(token)
