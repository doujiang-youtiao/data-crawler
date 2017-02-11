CREATE TABLE open_question
(
  id                  INT             NOT NULL ,
  question_text       VARCHAR(400)    NOT NULL ,
  CONSTRAINT pk_open_question PRIMARY KEY (id)
);

CREATE TABLE open_answer
(
  user_id             VARCHAR(40)     NOT NULL ,
  question_id         INT             NOT NULL ,
  answer_text         VARCHAR(2000)   NOT NULL ,
  CONSTRAINT pk_open_answer PRIMARY KEY (user_id, question_id),
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user_profile(id),
  CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES open_question(id)
);

CREATE TABLE user_profile
(
  id                  VARCHAR(40)     NOT NULL ,
  gender              VARCHAR(10) ,
  birthday_epoch      VARCHAR(20) ,
  zodiac              VARCHAR(20) ,
  chinese_zodiac      VARCHAR(20) ,
  height              VARCHAR(10) ,
  location            VARCHAR(100) ,
  city                VARCHAR(100) ,
  state               VARCHAR(100) ,
  country             VARCHAR(100) ,
  language            VARCHAR(100) ,
  education           VARCHAR(100) ,
  college             VARCHAR(100) ,
  graduate_school     VARCHAR(100) ,
  income              VARCHAR(20) ,
  company             VARCHAR(100) ,
  occupation          VARCHAR(100) ,
  job_title           VARCHAR(100) ,
  marital_status      VARCHAR(10) ,
  ethnicity           VARCHAR(40) ,
  body_type           VARCHAR(40) ,
  birth_country       VARCHAR(100) ,
  has_children        BOOL ,
  will_relocate       BOOL ,
  immigration         VARCHAR(20) ,
  first_arrive        VARCHAR(40) ,
  religion            VARCHAR(40) ,
  smoking             BOOL ,
  drinking            BOOL ,
  interest            VARCHAR(200) ,
  image_url           VARCHAR(500) ,
  CONSTRAINT pk_user_profile PRIMARY KEY (id)
);

CREATE TABLE target_profile
(
  user_id             VARCHAR(40)     NOT NULL ,
  gender              VARCHAR(10) ,
  max_age             INT ,
  min_age             INT ,
  height              VARCHAR(10) ,
  location            VARCHAR(100) ,
  language            VARCHAR(100) ,
  education           VARCHAR(100) ,
  income              VARCHAR(20) ,
  occupation          VARCHAR(100) ,
  marital_status      VARCHAR(10) ,
  ethnicity           VARCHAR(40) ,
  body_type           VARCHAR(40) ,
  birth_country       VARCHAR(100) ,
  has_children        BOOL ,
  immigration         VARCHAR(20) ,
  religion            VARCHAR(40) ,
  smoking             BOOL ,
  drinking            BOOL ,
  CONSTRAINT pk_target_profile PRIMARY KEY (user_id),
  CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES user_profile(id)
);