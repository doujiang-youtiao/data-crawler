import logging
import queue
from threading import Thread
from api_client import ApiClient
from repository import UserProfileRepository
from repository import TargetProfileRepository
from repository import OpenAnswerRepository


class Crawler:

    logger = logging.getLogger(name=__name__)

    def __init__(self, api_client):
        self.api_client = api_client

    def crawl(self):
        self.api_client.authenticate()
        api_account = self.api_client.api_account
        user_ids = self.api_client.get_user_list(n_per_page=20,
                                                 use_advanced=1,
                                                 page=api_account.pagination.get('current_page'),
                                                 pagination_token=api_account.pagination.get('token'),
                                                 cookies=api_account.cookies)
        self.logger.info('Crawling on page {}...found {} user(s).'
                         .format(api_account.pagination.get('current_page') - 1, len(user_ids)))

        if user_ids:
            threads = []
            user_queue = queue.Queue()

            for user_id in user_ids:
                thread = Thread(name=user_id,
                                target=ApiClient.get_user_thread,
                                args=[self.api_client, user_queue, user_id, False, True, True, api_account.cookies])
                self.logger.info('Crawling user {}...Start on thread {}'.format(user_id, thread.getName()))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
                self.logger.info('Crawling user...Complete on thread {}'.format(thread.getName()))

            del threads

            user_profile_repository = UserProfileRepository()
            target_profile_repository = TargetProfileRepository()
            open_answer_repository = OpenAnswerRepository()

            while user_queue.qsize() > 0:
                user = user_queue.get()
                user_profile = user.get('user_profile')
                target_profile = user.get('target_profile')
                open_answers = user.get('open_answers')
                # TODO: update existing entities
                if not user_profile_repository.profile_exists(user_profile):
                    user_profile_repository.insert_user_profile(user_profile)
                if not target_profile_repository.profile_exists(target_profile):
                    target_profile_repository.insert_target_profile(target_profile)
                if not False:
                    open_answer_repository.bulk_insert_open_answer(open_answers)
