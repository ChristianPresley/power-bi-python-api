#!/usr/bin/env python

cred_types = {
    'KEY': 'Key',
    'WINDOWS': 'Windows',
    'OAUTH2': 'OAuth2',
    'BASIC': 'Basic'
}

class Utils:
    def serialize_credentials(self, credentials_arr, cred_type):
        ''' Returns serialized credentials
        Args:
            credentials_arr (dict): Credentials based on the user input of the credentials type
            cred_type (string): Credentials type (i.e. Basic, Windows)
        Returns:
            string: Serialized credentials
        '''

        serialized_credentials = ''

        if cred_type == cred_types['KEY']:
            serialized_credentials = '{\'credentialData\':[{\'name\':\'key\',\'value\':\'' + credentials_arr[0] + '\'}]}'

        elif cred_type == cred_types['WINDOWS']:
            serialized_credentials = '{\'credentialData\':[{\'name\':\'username\',\'value\':\'' + \
                credentials_arr[0] + '\'},{\'name\':\'password\',\'value\':\'' + \
                credentials_arr[1] + '\'}]}'

        elif cred_type == cred_types['OAUTH2']:
            serialized_credentials = '{\'credentialData\':[{\'name\':\'accessToken\',\'value\':\'' + credentials_arr[0] + '\'}]}'

        elif cred_type == cred_types['BASIC']:
            serialized_credentials = '{\'credentialData\':[{\'name\':\'username\',\'value\':\'' + \
                credentials_arr[0] + '\'},{\'name\':\'password\',\'value\':\'' + \
                credentials_arr[1] + '\'}]}'

        else:
            raise Exception('Invalid credentials type')

        return serialized_credentials