from api_client import ApiClient
from domain import ApiAccount
import json   #added by c.wang

account = ApiAccount('greenbean@mailinator.com', 'greenbean')
client = ApiClient(account)

user_id  = client.get_user_list()[0]
user_json  = client.get_user_list()[1]

print(user_id)
#print("Length of user_id = ", len(user_id))

with open('response_json.json', 'w') as outfile:
    json.dump(user_json, outfile)

print(client.get_user(""))
# LenOfSeek = len(client.get_user("")["user_profile"][0])
# print("Length of element = ", LenOfSeek)

# Q1: Keys in response_json does not match variables defined in classes "UserProfile" and "TargetProfile"...
# Q2:get_user_list()turned out to have 20 user tokens, but get_user() returned only 12... am i missing something here?? please advise...