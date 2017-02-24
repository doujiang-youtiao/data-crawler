from api_client import ApiClient
from domain import ApiAccount
#import json

account = ApiAccount('greenbean@mailinator.com', 'greenbean')
client = ApiClient(account)

user_id = client.get_user_list()

user_profile_list=[]
target_profile_list=[]
open_answer_list=[]
for i in range(len(user_id)):
    user_profile_list.append(client.get_user(user_id[i])["user_profile"])
    target_profile_list.append(client.get_user(user_id[i])["target_profile"])
    open_answer_list.append(client.get_user(user_id[i])["open_answers"])

print ('User profile list is:', user_profile_list)
print ('Target profile list is:', target_profile_list)
print ('Open Answer List is:', open_answer_list)


first_user=user_profile_list[1].user_id
print('first user id', first_user)



# testing out the code with the 1st user token...
user_profile = client.get_user(user_id[0])["user_profile"]
target_profile = client.get_user(user_id[0])["target_profile"]
open_answer = client.get_user(user_id[0])["open_answers"]

image_url = user_profile.image_url_original
look_for_gender = target_profile.gender
OA_question_id = open_answer.question_id
OA_answer_text = open_answer.answer_text

print("User ID list : %s" % user_id)

print("URL of the the original image: %s ." % image_url, "\n""Gender the user looking for: %s." % look_for_gender)
print("Open answer question IDs:  %s ." % OA_question_id, "\n""Open answers : %s" % OA_answer_text)

