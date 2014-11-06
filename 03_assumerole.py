import boto.ec2
import boto.sts
import iam_utils

boto.set_stream_logger('goteamgo')
customers = {
    '540535557624': '2d6012e95f4942b9b5255274430a4ca2'
}

customer_id = '540535557624'
role_name = 'ModifyInstancesPolicy'
role_arn = 'arn:aws:iam::%s:role/%s' % (customer_id, role_name,)
sts_conn = boto.sts.STSConnection()
assumed_role = sts_conn.assume_role(role_arn, 'sec-403-demo2', external_id=customers[customer_id])
token = iam_utils.Token(assumed_role.credentials)
ec2_conn = boto.ec2.connect_to_region('us-west-2', **token.to_boto_dict())
print 'stopping', ec2_conn.stop_instances(['i-a458a3a8'])
