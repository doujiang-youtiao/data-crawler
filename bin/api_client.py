import logging
import threading
import requests
from domain import OpenAnswer
from domain import TargetProfile
from domain import UserProfile


class ApiClient:

    logger = logging.getLogger(name=__name__)

    urls = {
        'base': 'https://www.2redbeans.com',
        'auth': '/en/api/v2/user_sessions',
        'users': '/en/api/v2/users',
        'user': '/en/api/v2/users/{}'
    }

    def __init__(self, account):
        self.api_account = account
        self.lock = threading.RLock()

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
            self.logger.info('Authentication succeeded on account[%s]', username)
            self.__persist_cookie(cookies=response.cookies)
        elif response.status_code == 400:
            self.logger.error('Authentication failed on account[%s]', username)
            self.logger.error(response.json()['message'])
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
                    self.logger.error(err)
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
            user = response_json.get('user')

            up_language_id_list = self.__to_simple_list(dictionary=user.get('profile_details', {}).get('languages'),
                                                     list_key='values',
                                                     value_key='value')
            up_interest_id_list = self.__to_simple_list(dictionary=user.get('profile_details', {}).get('interests'),
                                                     list_key='values',
                                                     value_key='value')

            user_profile = UserProfile(
                user_id=user.get('token'),
                gender=user.get('sex'),
                birthday_epoch=user.get('birthday'),
                zodiac=user.get('profile_details', {}).get('zodiac', {}).get('text'),
                chinese_zodiac=user.get('profile_details', {}).get('cn_zodiac', {}).get('text'),
                height=user.get('profile_details', {}).get('height', {}).get('text'), # may not contain text by value
                location=user.get('location_short_description'),
                city=user.get('city'),
                state=user.get('state'),
                country=user.get('country'),
                language=up_language_id_list,
                education=user.get('profile_details', {}).get('education', {}).get('text'),
                college=user.get('profile_details', {}).get('college', {}).get('text'),
                graduate_school=user.get('profile_details', {}).get('grad_school', {}).get('text'),
                income=user.get('profile_details', {}).get('income', {}).get('text'),
                company=user.get('profile_details', {}).get('company', {}).get('text'),
                occupation=user.get('profile_details',{}).get('occupation',{}).get('text'),
                job_title=user.get('profile_details', {}).get('job_title', {}).get('text'),
                marital_status=user.get('profile_details', {}).get('marital_status', {}).get('text'),
                ethnicity=user.get('profile_details', {}).get('ethnicity', {}).get('text'),
                body_type=user.get('profile_details', {}).get('body_type', {}).get('text'),
                birth_country=user.get('profile_details', {}).get('birth_country', {}).get('text'),
                has_children=user.get('profile_details', {}).get('has_children', {}).get('text'),
                will_relocate=user.get('profile_details', {}).get('willing_to_relocate', {}).get('text'),
                immigration=user.get('profile_details', {}).get('immigration', {}).get('text'),
                first_arrive=user.get('profile_details', {}).get('first_arrive', {}).get('text'),
                religion=user.get('profile_details', {}).get('religion', {}).get('text'),
                smoking=user.get('profile_details', {}).get('smoking', {}).get('text'),
                drinking=user.get('profile_details', {}).get('drinking', {}).get('text'),
                interest=up_interest_id_list,
              ##  image_url_original=user.get('user_photos')[0].get('user_photo', {}).get('original_image_url'),##
                open_answers=[],
             )

            tp_language_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details', {}).get('language'),
                                                        list_key='values',
                                                        value_key='value')
            tp_education_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('education'),
                                                         list_key='values',
                                                         value_key='value')
            tp_income_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('income'),
                                                         list_key='values',
                                                         value_key='value')
            tp_occupation_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('occupation'),
                                                         list_key='values',
                                                         value_key='value')
            tp_marital_status_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('marital_status'),
                                                         list_key='values',
                                                         value_key='value')
            tp_ethnicity_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('ethnicity'),
                                                         list_key='values',
                                                         value_key='value')
            tp_body_type_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('body_type'),
                                                         list_key='values',
                                                         value_key='value')
            tp_birth_country_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('birth_country'),
                                                         list_key='values',
                                                         value_key='value')
            tp_has_children_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('has_children'),
                                                         list_key='values',
                                                         value_key='value')
            tp_immigration_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('immigration'),
                                                         list_key='values',
                                                         value_key='value')
            tp_religion_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('religion'),
                                                         list_key='values',
                                                         value_key='value')
            tp_smoking_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('smoking'),
                                                         list_key='values',
                                                         value_key='value')
            tp_drinking_id_list = self.__to_simple_list(dictionary=user.get('looking_for_details').get('drinking'),
                                                         list_key='values',
                                                         value_key='value')


            target_profile = TargetProfile(
                user_id=user.get('token'), # MUST
                gender=user.get('seeking'), #MUST
                max_age=user.get('looking_for_details', {}).get('age', {}).get('top'),
                min_age=user.get('looking_for_details', {}).get('age', {}).get('bottom'),
                height=user.get('looking_for_details', {}).get('height', {}).get('text'),
                location=user.get('looking_for_details').get('location', {}).get('values'),
                language=tp_language_id_list,
                education=tp_education_id_list,
                income=tp_income_id_list,
                occupation=tp_occupation_id_list,
                marital_status=tp_marital_status_id_list,
                ethnicity=tp_ethnicity_id_list,
                body_type=tp_body_type_id_list,
                birth_country=tp_birth_country_id_list,
                has_children=tp_has_children_id_list,
                immigration=tp_immigration_id_list,
                religion=tp_religion_id_list,
                smoking=tp_smoking_id_list,
                drinking=tp_drinking_id_list,
            )

            open_answers = []
            for item in user.get('open_answers', []):
                open_answer = OpenAnswer(user_id=user.get('token'),
                                         question_id=item.get('open_answer', {}).get('open_question', {}).get('id'),
                                         answer_text=item.get('open_answer', {}).get('answer'))
                open_answers.append(open_answer)

            return {"user_profile": user_profile, "target_profile": target_profile, "open_answers": open_answers}

        elif response.status_code == 404:
            if response_json.get('code') == 'record_not_found':
                try:
                    self.authenticate()
                except Exception as err:
                    self.logger.error(err)
                else:
                    return self.get_user(user_token=user_token, show_simple_options=show_simple_options,
                                         show_natural=show_natural, real_time_info=real_time_info,
                                         cookies=self.api_account.cookies)
            else:
                raise Exception('Unknown error - status: {}\tmessage: {}'.format(response.status_code, response_json))
        else:
            raise Exception('Unknown error - status: {}\tmessage: {}'.format(response.status_code, response_json))

    def get_user_thread(self, queue, user_token, show_simple_options=False, show_natural=True, real_time_info=True,
                        cookies=''):
        queue.put(self.get_user(user_token=user_token,
                                show_simple_options=show_simple_options,
                                show_natural=show_natural,
                                real_time_info=real_time_info,
                                cookies=cookies))

    def __update_pagination(self, current_page, token):
        with self.lock:
            self.api_account.pagination['current_page'] = current_page
            self.api_account.pagination['token'] = token

    def __persist_cookie(self, cookies):
        with self.lock:
            dict_cookies = cookies.get_dict()
            if 'AWSALB' in dict_cookies.keys() and 'user_credentials' in dict_cookies.keys():
                self.api_account.cookies['AWSALB'] = dict_cookies.get('AWSALB')
                self.api_account.cookies['user_credentials'] = dict_cookies.get('user_credentials')
                self.logger.info('User[%s]\'s cookies have been refreshed.', self.api_account.username)
            else:
                self.logger.warning('Response cookies do not have sufficient authentication attributes.')

    def __invalidate_account(self):
        with self.lock:
            self.api_account.valid = False
            raise Exception('Invalid api account[{}]'.format(self.api_account.username))

    @staticmethod
    def __to_simple_list(dictionary, list_key, value_key):
        simple_list = []
        if dictionary:
            complex_list = dictionary.get(list_key)
            if complex_list:
                for items in complex_list:
                    simple_list.append(items.get(value_key))
        return simple_list
