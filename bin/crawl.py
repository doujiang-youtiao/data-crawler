from api_client import ApiClient
from domain import ApiAccount
#import json

account = ApiAccount('greenbean@mailinator.com', 'greenbean')
client = ApiClient(account)

user_id = client.get_user_list()

# testing out the code with the 1st user token...
user_profile = client.get_user(user_id[0])["user_profile"]
target_profile = client.get_user(user_id[0])["target_profile"]
open_answer = client.get_user(user_id[0])["open_answers"]

gender = user_profile.gender
zodiac = user_profile.zodiac
look_for_gender = target_profile.gender
if open_answer:
    OA_question_id = open_answer[0].question_id
    OA_answer_text = open_answer[0].answer_text
else:
    OA_question_id = None
    OA_answer_text = None



print("User ID list : %s" % user_id)

print("Gender and zodiac of the user: %s and %s, respectively ." % (gender, zodiac), "\n""Gender the user looking for: %s." % look_for_gender)
print("Open answer question IDs:  %s ." % OA_question_id, "\n""Open answers : %s" % OA_answer_text)

