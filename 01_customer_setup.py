import boto.iam
import iam_utils

from awacs.aws import Allow, Policy, Statement, Action, AWSPrincipal
from awacs import ec2, iam, sts


access_policy = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[ec2.DescribeInstances, ec2.CreateTags],
            Resource=['*'],
        ),
    ]
)
print access_policy.to_json()

cloud_mgmt_platform_arn = iam.ARN('032298565451', 'root')
trust_policy = Policy(
    Statement=[
       Statement(
           Effect=Allow,
           Action=[sts.AssumeRole],
           Principal=AWSPrincipal(cloud_mgmt_platform_arn),
        ),
    ],
)
print trust_policy.to_json()

iam_conn = boto.iam.connect_to_region('us-west-2')
iam_utils.update_policy(
    iam_conn,
    'easy-describe',
    'easy-describe',
    trust_policy.to_json(),
    access_policy.to_json()
)
