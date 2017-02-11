class ApiAccount:

    def __init__(self, username, password, valid=True, cookies={}, pagination={}):
        self.username = username
        self.password = password
        self.valid = valid
        self.cookies = cookies
        self.pagination = pagination


class UserProfile:

    def __init__(self, user_id, gender=None, birthday_epoch=None, zodiac=None, chinese_zodiac=None, height=None,
                 location=None, city=None, state=None, country=None, language=None, education=None, college=None,
                 graduate_school=None, income=None, company=None, occupation=None, job_title=None, marital_status=None,
                 ethnicity=None, body_type=None, birth_country=None, has_children=None, will_relocate=None,
                 immigration=None, first_arrive=None, religion=None, smoking=None, drinking=None, interest=None,
                 image_url_original=None, about_me=None, open_answers=[]):
        self.user_id = user_id,
        self.gender = gender,
        self.birthday_epoch = birthday_epoch,
        self.zodiac = zodiac,
        self.chinese_zodiac = chinese_zodiac,
        self.height = height,
        self.location = location,
        self.birthday_epoch = birthday_epoch,
        self.city = city,
        self.state = state,
        self.country = country,
        self.language = language,
        self.education = education,
        self.college = college,
        self.graduate_school = graduate_school,
        self.income = income,
        self.company = company,
        self.occupation = occupation,
        self.job_title = job_title,
        self.marital_status = marital_status,
        self.ethnicity = ethnicity,
        self.body_type = body_type,
        self.birth_country = birth_country,
        self.has_children = has_children,
        self.will_relocate = will_relocate,
        self.immigration = immigration,
        self.first_arrive = first_arrive,
        self.religion = religion,
        self.smoking = smoking,
        self.drinking = drinking,
        self.interest = interest,
        self.image_url_original = image_url_original,
        self.about_me = about_me,
        self.open_answers = open_answers


class TargetProfile:

    def __init__(self, user_id, gender=None, max_age=80, min_age=18, height=None, location=None, language=None,
                 education=None, income=None, occupation=None, marital_status=None, ethnicity=None, body_type=None,
                 birth_country=None, has_children=None, immigration=None, religion=None, smoking=None, drinking=None):
        self.user_id = user_id,
        self.gender = gender,
        self.max_age = max_age,
        self.min_age = min_age,
        self.height = height,
        self.location = location,
        self.language = language,
        self.education = education,
        self.income = income,
        self.occupation = occupation,
        self.marital_status = marital_status,
        self.ethnicity = ethnicity,
        self.body_type = body_type,
        self.birth_country = birth_country,
        self.has_children = has_children,
        self.immigration = immigration,
        self.religion = religion,
        self.smoking = smoking,
        self.drinking = drinking
