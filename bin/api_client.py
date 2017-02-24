import logging
import requests
from domain import OpenAnswer
from domain import TargetProfile
from domain import UserProfile


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
            user = response_json["user"]

            user_profile = UserProfile(
                user_id = user["token"],
                gender = user["sex"],
                birthday_epoch = user["birthday"],
                # zodiac = user["profile_details"]["zodiac"]["value"],
                zodiac = user["profile_details"]["zodiac"],
                # chinese_zodiac = user["profile_details"]["cn_zodiac"]["value"],
                chinese_zodiac = user["profile_details"]["cn_zodiac"],
                # height = user["profile_details"]["height"]["value"], # may not have text. value only??
                location = user["location_short_description"],
                city = user["city"],
                state = user["state"],
                country = user["country"],
                # language = user["profile_details"]["languages"]["values"]["value"], #May contain one or more value, considering changing this to a list?
                language = user["profile_details"]["languages"],
                # education = user["profile_details"]["education"]["value"],
                education = user["profile_details"]["education"],
                # college = user["profile_details"]["college"]["value"],
                college = user["profile_details"]["college"],
                # graduate_school = user["profile_details"]["grad_school"]["value"],
                 graduate_school = user["profile_details"]["grad_school"],
                # income = user["profile_details"]["income"]["value"],
                income = user["profile_details"]["income"],
                # company = user["profile_details"]["company"]["value"], # May not have a value or text
                company = user["profile_details"]["company"],
                # occupation = user["profile_details"]["occupation"]["value"],
                occupation = user["profile_details"]["occupation"],
                # job_title = user["profile_details"]["job_title"]["label"], # May not have a value or text
                job_title = user["profile_details"]["job_title"],
                # marital_status = user["profile_details"]["marital_status"]["value"],
                marital_status = user["profile_details"]["marital_status"],
                # ethnicity = user["profile_details"]["ethnicity"]["value"],
                ethnicity = user["profile_details"]["ethnicity"],
                # body_type = user["profile_details"]["body_type"]["value"],
                body_type = user["profile_details"]["body_type"],
                # birth_country = user["profile_details"]["birth_country"]["value"],
                birth_country = user["profile_details"]["birth_country"],
                # has_children = user["profile_details"]["has_children"]["value"],
                has_children = user["profile_details"]["has_children"],
                # will_relocate = user["profile_details"]["willing_to_relocate"]["value"],
                will_relocate = user["profile_details"]["willing_to_relocate"],
                # immigration = user["profile_details"]["immigration"]["value"],
                immigration = user["profile_details"]["immigration"],
                # first_arrive = user["profile_details"]["first_arrive"]["value"],
                first_arrive = user["profile_details"]["first_arrive"],
                # religion = user["profile_details"]["religion"]["value"],
                religion = user["profile_details"]["religion"],
                # smoking = user["profile_details"]["smoking"]["value"],
                smoking = user["profile_details"]["smoking"],
                #drinking = user["profile_details"]["drinking"]["value"],
                drinking = user["profile_details"]["drinking"],
                # interest = user["profile_details"]["interests"]["values"],#May contain one or more value, considering changing this to a list?
                interest = user["profile_details"]["interests"],
                image_url_original = user["user_photos"][0]["user_photo"]["original_image_url"]
                # open_answers = user["open_answers"],
            )

            target_profile = TargetProfile(
                user_id = user["token"],
                gender = user["seeking"]
                # max_age = user["looking_for_details"]["age"]["top"],
                # min_age = user["looking_for_details"]["age"]["bottom"],
                # height = user["looking_for_details"]["height"]["text"],     # may contain max and min req. as well like age.
                # location = user["looking_for_details"]["location"]["importance"]["value"],
                # language = user["looking_for_details"]["location"]["importance"]["value"],
                # education = user["looking_for_details"]["education"], # may not contain any value
                # income = user["looking_for_details"]["income"]["importance"]["value"],
                # occupation = user["looking_for_details"]["occupation"]["importance"]["value"],
                # marital_status = user["looking_for_details"]["marital_status"]["values"][0]["text"],
                # ethnicity = user["looking_for_details"]["ethnicity"]["values"][0]["text"],
                # body_type = user["looking_for_details"]["body_type"],    # May contain one or more value, considering changing this to a list?
                # birth_country = user["looking_for_details"]["birth_country"]["importance"]["value"],
                # has_children = user["looking_for_details"]["has_children"], # # May not have a value or text
                # immigration = user["looking_for_details"]["immigration"]["importance"]["value"],
                # religion = user["looking_for_details"]["religion"]["importance"]["value"],
                # smoking = user["looking_for_details"]["smoking"]["values"][0]["value"],
                # drinking = user["looking_for_details"]["drinking"]["values"][0]["value"],
            )

            num_open_answer = len(user["open_answers"])
            id_list = []
            question_list = []
            answer_list = []
            if num_open_answer != 0:
                for idx in range(num_open_answer):
                    id_list.append(user["open_answers"][idx]["open_answer"]["open_question"]["id"])
                    question_list.append(user["open_answers"][idx]["open_answer"]["open_question"]["description"])
                    answer_list.append(user["open_answers"][idx]["open_answer"]["answer"])
            # else:

            open_answers = OpenAnswer(
                user_id = user["token"],
                question_id = id_list,
                answer_text = answer_list,
                # question_text = question_list            # consider adding "open questions" into the class def?
            )
            return {"user_profile": user_profile, "target_profile": target_profile, "open_answers": open_answers}
            # ========================================added code below==========================================#

        elif response.status_code == 404:
            try:
                self.authenticate()
            except Exception as err:
                logging.error(err)
            else:
                return self.get_user(user_token=user_token, show_simple_options=show_simple_options,
                                     show_natural=show_natural, real_time_info=real_time_info,
                                     cookies=self.api_account.cookies)
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
