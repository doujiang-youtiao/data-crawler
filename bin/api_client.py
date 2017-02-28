import requests
import logging
from domain import UserProfile
from domain import TargetProfile
from domain import OpenAnswer
# import json

class ApiClient:

    urls = {
        'base': 'https://www.2redbeans.com',
        'auth': '/en/api/v2/user_sessions',
        'users': '/en/api/v2/users',
        'user': '/en/api/v2/users/{}'
    }

    def __init__(self, account):
        self.api_account = account

    def authenticate(self):
        username = self.api_account.username
        password = self.api_account.password

        request_url = ApiClient.urls['base'] + ApiClient.urls['auth']
        request_headers = {
            'cache-control': 'no-cache',
            'content-type': 'multipart/form-data',
            'pragma': 'no-cache',
            'referer': 'https://www.2redbeans.com/en/app/login',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36',
            'x-2rb-webview': '2RedBeans/1.0 WebView-1/1.0.1 (Browser; Masque 1.0; locale en_US)'
        }
        request_payload = {
            'user_session[email]': username,
            'user_session[password]': password
        }

        response = requests.post(url=request_url, headers=request_headers, data=request_payload)

        if response.status_code == 200:
            logging.info('Authentication succeeded on account[%s]', username)
            self.__persist_cookie(cookies=response.cookies)
        elif response.status_code == 400:
            logging.error('Authentication failed on account[%s]', username)
            logging.error(response.json()['message'])
            self.__invalidate_account()
        else:
            return

    def get_user_list(self, n_per_page=20, use_advanced=1, page=None, pagination_token=None, cookies=''):
        request_url = ApiClient.urls['base'] + ApiClient.urls['users']
        request_headers = {
            'accept': 'application/json, text/plain, */*',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.2redbeans.com/en/app/search',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36',
            'x-2rb-webview': '2RedBeans/1.0 WebView-1/1.0.1 (Browser; Masque 1.0; locale en_US)'
        }
        query_parameters = {
            'n_per_page': n_per_page,
            'use_advanced': use_advanced,
            'page': page,
            'pagination_token': pagination_token
        }

        response = requests.get(url=request_url, headers=request_headers, params=query_parameters, cookies=cookies)
        response_json = response.json()

        if response.status_code == 200:
            user_list = []
            for user in response_json['users']:
                user_list.append(user['user']['token'])
            self.__update_pagination(current_page=response_json['next_page'], token=response_json['pagination_token'])
            return user_list
        elif response.status_code == 400:
            if response_json['code'] == 'login_required':
                try:
                    self.authenticate()
                except Exception as err:
                    logging.error(err)
                else:
                    return self.get_user_list(n_per_page=n_per_page, use_advanced=use_advanced, page=page,
                                              pagination_token=pagination_token, cookies=self.api_account.cookies)
            else:
                logging.error('Unknown error - status: %s\tmessage: %s', response.status_code, response_json)
        else:
            logging.error('Unknown error - status: %s\tmessage: %s', response.status_code, response_json)

    def get_user(self, user_token, show_simple_options=False, show_natural=True, real_time_info=True, cookies=''):
        request_url = (ApiClient.urls['base'] + ApiClient.urls['user']).format(user_token)
        request_headers = {
            'accept': 'application/json, text/plain, */*',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://www.2redbeans.com/en/app/profile/{}'.format(user_token),
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/56.0.2924.87 Safari/537.36',
            'x-2rb-webview': '2RedBeans/1.0 WebView-1/1.0.1 (Browser; Masque 1.0; locale en_US)'
        }
        query_parameters = {
            'show_simple_options': show_simple_options,
            'show_natural': show_natural,
            'real_time_info': real_time_info
        }

        response = requests.get(url=request_url, headers=request_headers, params=query_parameters, cookies=cookies)
        response_json = response.json()

        if response.status_code == 200:
            # ========================================added code below==========================================#
            # response_json_out = open("response_json.json", "w")
            # json.dump(response_json, response_json_out)

            user = response_json.get("user")

            user_profile = UserProfile(
                user_id=user.get("token"),
                gender=user.get("sex", None),
                birthday_epoch=user.get("birthday"),
                zodiac=user.get("profile_details").get("zodiac").get("text", None),
                chinese_zodiac=user.get("profile_details").get("cn_zodiac").get("text", None),
                height=user.get("profile_details").get("height").get("text", None),
                location=user.get("location_short_description", None),
                city=user.get("city", None),
                state=user.get("state", None),
                country=user.get("country", None),
                # language=[],
                education=user.get("profile_details").get("education").get("text", None),
                college=user.get("profile_details").get("college").get("text", None),
                graduate_school=user.get("profile_details").get("grad_school").get("text", None),
                income=user.get("profile_details").get("income").get("text", None),
                company=user.get("profile_details").get("company").get("text", None),
                occupation=user.get("profile_details").get("occupation").get("text", None),
                job_title=user.get("profile_details").get("job_title").get("text", None),
                marital_status=user.get("profile_details").get("marital_status").get("text", None),
                ethnicity=user.get("profile_details").get("ethnicity").get("text", None),
                body_type=user.get("profile_details").get("body_type").get("text", None),
                birth_country=user.get("profile_details").get("birth_country").get("text", None),
                has_children=user.get("profile_details").get("has_children").get("text", None),
                will_relocate=user.get("profile_details").get("willing_to_relocate").get("text", None),
                immigration=user.get("profile_details").get("immigration").get("text", None),
                first_arrive=user.get("profile_details").get("first_arrive").get("text", None),
                religion=user.get("profile_details").get("religion").get("text", None),
                smoking=user.get("profile_details").get("smoking").get("text", None),
                drinking=user.get("profile_details").get("drinking").get("text", None),
                # interest=[],
                image_url_original=user.get("user_photos")[0].get("user_photo").get("original_image_url", None),
                # open_answers=[],
            )

            target_profile = TargetProfile(
                user_id=user["token"],
                gender=user.get("seeking", None),
                max_age=user.get("looking_for_details").get("age").get("top", None),
                min_age=user.get("looking_for_details").get("age").get("bottom", None),
                height=user.get("looking_for_details").get("height").get("text", None), # why not set a max and min like for age?
                # location=user.get("looking_for_details").get("location").get("importance").get("text", None),
                # language=user.get("looking_for_details").get("language").get("importance").get("text", None),
                education=user.get("looking_for_details").get("education").get("importance", None),   #nested dict problem
                # income=user.get("looking_for_details").get("income").get("importance").get("text", None),   #nested dict problem
                # occupation=user.get("looking_for_details").get("occupation").get("importance").get("text", None),  #nested dict problem
                # marital_status=user.get("looking_for_details").get("marital_status"),
                # ethnicity=user.get("looking_for_details").get("ethnicity"),
                # body_type=user.get("looking_for_details").get("body_type"),
                # birth_country=user.get("looking_for_details").get("birth_country").get("importance").get("text", None),#nested dict problem
                # has_children=user.get("looking_for_details").get("has_children").get("importance").get("text", None),#nested dict problem
                # immigration=user.get("looking_for_details").get("immigration").get("importance").get("text", None),   #nested dict problem
                # religion=user.get("looking_for_details").get("religion").get("importance").get("text", None),    #nested dict problem
                # smoking=user.get("looking_for_details").get("smoking"),
                # drinking=user.get("looking_for_details").get("drinking"),
            )

            num_open_answer = len(user["open_answers"])
            open_answers = []
            if num_open_answer:
                for idx in range(num_open_answer):
                    open_answers.append(
                        OpenAnswer(
                            user_id = user["open_answers"][idx]["open_answer"]["open_question"]["id"],
                            question_id = user["open_answers"][idx]["open_answer"]["open_question"]["description"],
                            answer_text = user["open_answers"][idx]["open_answer"]["answer"]
                        )
                    )
            # else:
            #     open_answers = None

            return {"user_profile": user_profile, "target_profile": target_profile, "open_answers": open_answers}

        elif response.status_code == 404:
            if response_json['code'] == 'record_not_found':
                try:
                    self.authenticate()
                except Exception as err:
                    logging.error(err)
                else:
                    return self.get_user(user_token=user_token, show_simple_options=show_simple_options,
                                         show_natural=show_natural, real_time_info=real_time_info,
                                         cookies=self.api_account.cookies)
            else:
                logging.error('Unknown error - status: %s\tmessage: %s', response.status_code, response_json)
        else:
            logging.error('Unknown error - status: %s\tmessage: %s', response.status_code, response_json)


    def __update_pagination(self, current_page, token):
        self.api_account.pagination['current_page'] = current_page
        self.api_account.pagination['token'] = token

    def __persist_cookie(self, cookies):
        dict_cookies = cookies.get_dict()
        if dict_cookies.__contains__('AWSALB') and dict_cookies.__contains__('user_credentials'):
            self.api_account.cookies['AWSALB'] = dict_cookies.get('AWSALB')
            self.api_account.cookies['user_credentials'] = dict_cookies.get('user_credentials')
            logging.info('User[%s]\'s cookies have been refreshed.', self.api_account.username)
        else:
            logging.warning('Response cookies do not have sufficient authentication attributes.')

    def __invalidate_account(self):
        self.api_account.valid = False
        raise Exception('Invalid api account[{}]'.format(self.api_account.username))
