"""Customer side setup for example 3 in sec-403 at reinvent 2014.

This script sets up roles with appropriate access policies and trust policies
for two features of a hypothetical application. In one case we want a role that
only grants DescribeInstances permission and in another case we want the option
to Stop and StartInstances as well. We have two separate roles because we
intend to use these roles from different places in our application. In the
readonly case we know that our application only needs read access so we provide
it with only that access.
"""
import boto.iam
import iam_utils

from awacs.aws import Allow, Policy, Statement, Action, AWSPrincipal
from awacs import ec2, iam, sts

cloud_mgmt_platform_acct_id = '032298565451'
cloud_mgmt_platform_arn = iam.ARN(cloud_mgmt_platform_acct_id, 'root')

readonly_access_policy = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[ec2.DescribeInstances],
            Resource=['*'],
        ),
    ]
)

modifyinstances_access_policy = Policy(
    Statement=[
        Statement(
            Effect=Allow,
            Action=[ec2.RunInstances, ec2.StopInstances],
            Resource=['*'],
        ),
    ]
)

# This trust policy is fairly liberal. The customer is trusting us, the cloud
# management platform, to not abuse the policy and put their resources at risk.
# This policy says anything that matches the cloud_mgmt_platform_arn is allowed
# to assume this role. We could, if we wanted, launch a public web server with
# credentials to call AssumeRole and thus assume the roles tied to this trust
# policy. If that web server were then compromised these roles could then,
# easily, be assumed by an attacker and used to mount an attack against one of
# our customers. This is bad, and our customer trusts us to do better. We will
# not launch a public web server with the ability to assume these roles.
cloud_mgmt_platform_trust_policy = Policy(
    Statement=[
       Statement(
           Effect=Allow,
           Action=[sts.AssumeRole],
           Principal=AWSPrincipal(cloud_mgmt_platform_arn),
        ),
    ],
)

iam_conn = boto.iam.connect_to_region('universal')
iam_utils.update_policy(
    iam_conn,
    'ReadonlyPolicy',
    'ReadonlyPolicy',
    cloud_mgmt_platform_trust_policy.to_json(),
    readonly_access_policy.to_json()
)

iam_utils.update_policy(
    iam_conn,
    'ModifyInstancesPolicy',
    'ModifyInstancesPolicy',
    cloud_mgmt_platform_trust_policy.to_json(),
    modifyinstances_access_policy.to_json()
)
