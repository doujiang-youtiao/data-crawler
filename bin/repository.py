import mysql.connector as ds


class DataSource:

    host = ''
    username = ''
    password = ''
    database = ''

    def open_connection(self):
        return ds.connect(host=self.host, user=self.username, passwd=self.password, db=self.database)


class UserProfileRepository:

    datasource = DataSource()

    def profile_exists(self, user_profile):
        connection = self.datasource.open_connection()
        cursor = connection.cursor()
        prepared_sql = """SELECT count(*) FROM user_profile WHERE id = {user_id};"""
        sql_command = prepared_sql.format(user_profile.user_id)
        cursor.execute(sql_command)
        result = cursor.fetchone()
        return result[0] > 0

    def insert_user_profile(self, user_profile):
        connection = self.datasource.open_connection()
        cursor = connection.cursor()
        prepared_sql = """INSERT INTO user_profile (
                       id, gender, birthday_epoch, zodiac, chinese_zodiac, height, location, city, state, country,
                       language, education, college, graduate_school, income, company, occupation, job_title,
                       marital_status, ethnicity, body_type, birth_country, has_children, will_relocate, immigration,
                       first_arrive, religion, smoking, drinking, interest, image_url)
                       VALUES (
                       {user_id}, {gender}, {birthday_epoch}, {zodiac}, {chinese_zodiac}, {height}, {location}, {city},
                       {state}, {country}, {language}, {education}, {college}, {graduate_school}, {income}, {company},
                       {occupation}, {job_title}, {marital_status}, {ethnicity}, {body_type}, {birth_country},
                       {has_children}, {will_relocate}, {immigration}, {first_arrive}, {religion}, {smoking},
                       {drinking}, {interest}, {image_url});"""
        sql_command = prepared_sql.format(user_id=user_profile.user_id, gender=user_profile.gender,
                                          birthday_epoch=user_profile.birthday_epoch, zodiac=user_profile.zodiac,
                                          chinese_zodiac=user_profile.chinese_zodiac, height=user_profile.height,
                                          location=user_profile.location, city=user_profile.city,
                                          state=user_profile.state, country=user_profile.country,
                                          language=user_profile.language, education=user_profile.education,
                                          college=user_profile.college, graduate_school=user_profile.graduate_school,
                                          income=user_profile.income, company=user_profile.company,
                                          occupation=user_profile.occupation, job_title=user_profile.job_title,
                                          marital_status=user_profile.marital_status, ethnicity=user_profile.ethnicity,
                                          body_type=user_profile.body_type, birth_country=user_profile.birth_country,
                                          has_children=user_profile.has_children,
                                          will_relocate=user_profile.will_relocate,
                                          immigration=user_profile.immigration,
                                          first_arrive=user_profile.first_arrive, religion=user_profile.religion,
                                          smoking=user_profile.smoking, drinking=user_profile.drinking,
                                          interest=user_profile.interest, image_url=user_profile.image_url_original)
        cursor.execute(sql_command)
        connection.commit()
        cursor.close()
        connection.close()


class TargetProfileRepository:

    datasource = DataSource()

    def profile_exists(self, target_profile):
        connection = self.datasource.open_connection()
        cursor = connection.cursor()
        prepared_sql = """SELECT count(*) FROM target_profile WHERE user_id = {user_id};"""
        sql_command = prepared_sql.format(target_profile.user_id)
        cursor.execute(sql_command)
        result = cursor.fetchone()
        return result[0] > 0

    def insert_target_profile(self, target_profile):
        connection = self.datasource.open_connection()
        cursor = connection.cursor()
        prepared_sql = """INSERT INTO target_profile (
                       user_id, gender, max_age, min_age, height, location, language, education, income, occupation,
                       marital_status, ethnicity, body_type, birth_country, has_children, will_relocate, immigration,
                       religion, smoking, drinking)
                       VALUES (
                       {user_id}, {gender}, {max_age}, {min_age}, {height}, {location}, {language}, {education},
                       {income}, {occupation}, {marital_status}, {ethnicity}, {body_type}, {birth_country},
                       {has_children}, {will_relocate}, {immigration}, {religion}, {smoking}, {drinking});"""
        sql_command = prepared_sql.format(user_id=target_profile.user_id, gender=target_profile.gender,
                                          max_age=target_profile.max_age, min_age=target_profile.min_age,
                                          height=target_profile.height, location=target_profile.location,
                                          language=target_profile.language, education=target_profile.education,
                                          income=target_profile.income, occupation=target_profile.occupation,
                                          marital_status=target_profile.marital_status,
                                          ethnicity=target_profile.ethnicity, body_type=target_profile.body_type,
                                          birth_country=target_profile.birth_country,
                                          has_children=target_profile.has_children,
                                          will_relocate=target_profile.will_relocate,
                                          immigration=target_profile.immigration, religion=target_profile.religion,
                                          smoking=target_profile.smoking, drinking=target_profile.drinking)
        cursor.execute(sql_command)
        connection.commit()
        cursor.close()
        connection.close()
