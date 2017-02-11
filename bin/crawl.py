from api_client import ApiClient
from domain import ApiAccount


account = ApiAccount('greenbean@mailinator.com', 'greenbean')
client = ApiClient(account)
print(client.get_user_list())