import logging
import requests
from domain import OpenAnswer
from domain import TargetProfile
from domain import UserProfile

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
        self.logger = logging.Logger(name='ApiClient', level=logging.INFO)

    def authenticate(self):
        username = self.api_account.username
        password = self.api_account.password

        request_url = ApiClient.urls.get('base') + ApiClient.urls.get('auth')
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
        response_json = response.json()

        if response.status_code == 200:
            logging.info('Authentication succeeded on account[%s]', username)
            self.__persist_cookie(cookies=response.cookies)
        elif response.status_code == 400:
            logging.error('Authentication failed on account[%s]', username)
            logging.error(response.json()['message'])
            self.__invalidate_account()
        else:
            raise Exception('Unknown error - status: {}\tmessage: {}'.format(response.status_code, response_json))

    def get_user_list(self, n_per_page=20, use_advanced=1, page=None, pagination_token=None, cookies=''):
        request_url = ApiClient.urls.get('base') + ApiClient.urls.get('users')
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
            for user in response_json.get('users'):
                user_list.append(user.get('user').get('token'))
            self.__update_pagination(current_page=response_json.get('next_page'), token=response_json.get('pagination_token'))
            return user_list
        elif response.status_code == 400:
            if response_json.get('code') == 'login_required':
                try:
                    self.authenticate()
                except Exception as err:
                    logging.error(err)
                else:
                    return self.get_user_list(n_per_page=n_per_page, use_advanced=use_advanced, page=page,
                                              pagination_token=pagination_token, cookies=self.api_account.cookies)
            else:
                raise Exception('Unknown error - status: {}\tmessage: {}'.format(response.status_code, response_json))
        else:
            raise Exception('Unknown error - status: {}\tmessage: {}'.format(response.status_code, response_json))

    def get_user(self, user_token, show_simple_options=False, show_natural=True, real_time_info=True, cookies=''):
        request_url = (ApiClient.urls.get('base') + ApiClient.urls.get('user')).format(user_token)
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

            def multi_option(input_values):
                multi_answer = []
                if input_values:
                    for idx in range(len(input_values)):
                        multi_answer.append(input_values[idx].get("text"))
                return multi_answer

            user_profile = UserProfile(
                user_id=user.get("token"),
                gender=user.get("sex"),
                birthday_epoch=user.get("birthday"),
                zodiac=user.get("profile_details").get("zodiac").get("text"),
                chinese_zodiac=user.get("profile_details").get("cn_zodiac").get("text"),
                height=user.get("profile_details").get("height").get("text"),
                location=user.get("location_short_description"),
                city=user.get("city"),
                state=user.get("state"),
                country=user.get("country"),
                language=multi_option(user.get("profile_details").get("languages").get("values")),
                education=user.get("profile_details").get("education").get("text"),
                college=user.get("profile_details").get("college").get("text"),
                graduate_school=user.get("profile_details").get("grad_school").get("text"),
                income=user.get("profile_details").get("income").get("text"),
                company=user.get("profile_details").get("company").get("text"),
                occupation=user.get("profile_details").get("occupation").get("text"),
                job_title=user.get("profile_details").get("job_title").get("text"),
                marital_status=user.get("profile_details").get("marital_status").get("text"),
                ethnicity=user.get("profile_details").get("ethnicity").get("text"),
                body_type=user.get("profile_details").get("body_type").get("text"),
                birth_country=user.get("profile_details").get("birth_country").get("text"),
                has_children=user.get("profile_details").get("has_children").get("text"),
                will_relocate=user.get("profile_details").get("willing_to_relocate").get("text"),
                immigration=user.get("profile_details").get("immigration").get("text"),
                first_arrive=user.get("profile_details").get("first_arrive").get("text"),
                religion=user.get("profile_details").get("religion").get("text"),
                smoking=user.get("profile_details").get("smoking").get("text"),
                drinking=user.get("profile_details").get("drinking").get("text"),
                interest=multi_option(user.get("profile_details").get("interests").get("values")),
                image_url_original=user.get("user_photos")[0].get("user_photo").get("original_image_url"),
                # open_answers=[],
            )

            target_profile = TargetProfile(
                user_id=user.get("token"), # MUST
                gender=user.get("seeking"), #MUST
                max_age=user.get("looking_for_details").get("age").get("top"), #MUST
                min_age=user.get("looking_for_details").get("age").get("bottom"),   #MUST
                height=user.get("looking_for_details").get("height").get("text"), #MUST
                location=user.get("looking_for_details").get("location").get("values"), #NO INFO
                language=multi_option(user.get("looking_for_details").get("languages").get("values")), #Multi or No preference
                education=multi_option(user.get("looking_for_details").get("education").get("values")),   #Lable only or contains a value
                income=multi_option(user.get("looking_for_details").get("income").get("values")), #Multi or No preference
                occupation=multi_option(user.get("looking_for_details").get("occupation").get("values")),  #Multi or No preference
                marital_status=multi_option(user.get("looking_for_details").get("marital_status").get("values")), #Multi or No preference
                ethnicity=multi_option(user.get("looking_for_details").get("ethnicity").get("values")), #Multi or No preference
                body_type=multi_option(user.get("looking_for_details").get("body_type").get("values")), #Multi or No preference
                birth_country=user.get("looking_for_details").get("birth_country").get("values"), #NO INFO
                has_children=multi_option(user.get("looking_for_details").get("has_children").get("values")), #Multi or No preference
                immigration=multi_option(user.get("looking_for_details").get("immigration").get("values")),   #Multi or No preference
                religion=multi_option(user.get("looking_for_details").get("religion").get("values")),    #Multi or No preference
                smoking=multi_option(user.get("looking_for_details").get("smoking").get("values")), #Multi or No preference
                drinking=multi_option(user.get("looking_for_details").get("drinking").get("values")), #Multi or No preference
            )

            open_answer = user.get("open_answers")
            open_answers = []
            if open_answer:
                for idx in range(len(open_answer)):
                    open_answers.append(
                        OpenAnswer(
                            user_id = user.get("token"),
                            question_id = open_answer[idx].get("open_answer").get("open_question").get("description"),
                            answer_text = open_answer[idx].get("open_answer").get("answer")
                        )
                    )
            return {"user_profile": user_profile, "target_profile": target_profile, "open_answers": open_answers}

        elif response.status_code == 404:
            if response_json.get('code') == 'record_not_found':
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
            raise Exception('Unknown error - status: {}\tmessage: {}'.format(response.status_code, response_json))

    def __update_pagination(self, current_page, token):
        self.api_account.pagination['current_page'] = current_page
        self.api_account.pagination['token'] = token

    def __persist_cookie(self, cookies):
        dict_cookies = cookies.get_dict()
        if 'AWSALB' in dict_cookies.keys() and 'user_credentials' in dict_cookies.keys():
            self.api_account.cookies['AWSALB'] = dict_cookies.get('AWSALB')
            self.api_account.cookies['user_credentials'] = dict_cookies.get('user_credentials')
            logging.info('User[%s]\'s cookies have been refreshed.', self.api_account.username)
        else:
            logging.warning('Response cookies do not have sufficient authentication attributes.')

    def __invalidate_account(self):
        self.api_account.valid = False
        raise Exception('Invalid api account[{}]'.format(self.api_account.username))
