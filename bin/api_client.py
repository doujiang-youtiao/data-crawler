import requests
import logging


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

        response = requests.post(request_url, headers=request_headers, data=request_payload)

        if response.status_code == 200:
            logging.info('Authentication succeeded on account[%s]', username)
            self.__persist_cookie(response.cookies)
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

        response = requests.get(request_url, headers=request_headers, params=query_parameters, cookies=cookies)
        response_json = response.json()

        if response.status_code == 200:
            user_list = []
            for user in response_json['users']:
                user_list.append(user['user']['token'])
            self.__update_pagination(response_json['next_page'], response_json['pagination_token'])
            return user_list
        elif response.status_code == 400:
            if response_json['code'] == 'login_required':
                try:
                    self.authenticate()
                except Exception as err:
                    logging.error(err)
                else:
                    return self.get_user_list(
                        n_per_page, use_advanced, page, pagination_token, self.api_account.cookies)
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

        response = requests.get(request_url, headers=request_headers, params=query_parameters, cookies=cookies)
        response_json = response.json()

        if response.status_code == 200:
            return
        elif response.status_code == 400:
            if response_json['code'] == 'login_required':
                try:
                    self.authenticate()
                except Exception as err:
                    logging.error(err)
                else:
                    return self.get_user(
                        user_token, show_simple_options, show_natural, real_time_info, self.api_account.cookies)
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
