from api_client import ApiClient

account = {
    'username': 'greenbean@mailinator.com',
    'password': 'greenbean',
    'valid': True,
    'cookies': {},
    'pagination': {}
}

client = ApiClient(account)
print(client.get_user_list())