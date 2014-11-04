import urllib

from boto.exception import BotoServerError


class Token(object):
    def __init__(self, credentials):
        self.credentials = credentials

    def to_boto_dict(self):
        return {
            'aws_access_key_id': self.access_key,
            'aws_secret_access_key': self.secret_key,
            'security_token': self.session_token,
        }

    @property
    def access_key(self):
        return self.credentials.access_key

    @property
    def secret_key(self):
        return self.credentials.secret_key

    @property
    def session_token(self):
        return self.credentials.session_token


def update_policy(conn, role, policy_name, trust, new_policy, profile=False):
    try:
        if role not in [x.role_name for x in conn.list_roles().roles]:
            print 'Adding %s role' % (role,)
            conn.create_role(role, trust)
            conn.put_role_policy(role, policy_name, new_policy)
            return
        else:
            print 'Role %s already exists, will check policies' % (role,)

        no_policy = False
        try:
            # Get current policy
            policy = conn.get_role_policy(role, policy_name)

            # Get the policy document
            old_policy = policy['get_role_policy_response']
            old_policy = old_policy['get_role_policy_result']
            old_policy = old_policy['policy_document']
        except BotoServerError, e:
            if e.code != 'NoSuchEntity':
                raise
            print 'No policy for role %s' % (role,)
            no_policy = True

        # Update if it needs it
        if no_policy or new_policy != urllib.unquote(old_policy):
            print 'Updating %s policy' % (role,)
            conn.put_role_policy(role, policy_name, new_policy)
        else:
            print 'Role %s policy up-to-date' % (role,)

        # See if we need to add an instance profile
        if profile:
            # Get the list of instance profiles for this role name
            profiles = conn.list_instance_profiles_for_role(role)
            profiles = profiles['list_instance_profiles_for_role_response']
            profiles = profiles['list_instance_profiles_for_role_result']
            profiles = profiles['instance_profiles']

            # Check to see if we should create the instance profile
            profile_names = [i.instance_profile_name for i in profiles]
            if role not in profile_names:
                conn.create_instance_profile(role)
                conn.add_role_to_instance_profile(role, role)
    except BotoServerError, e:
        if e.code != 'AccessDenied':
            raise
        print 'Access denied for %s' % (role,)
