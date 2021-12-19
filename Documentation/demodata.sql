/* This is used to create demo-data for the application */

INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '1234-12345678', false);
INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '2234-12345678', false);
INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '3234-12345678', false);
INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '4234-12345678', false);

INSERT INTO tsohaproject.additionaltrainings (training, description, active) VALUES ('Mental Health', 'A basic training on adolescense and mental health.', 'True');
INSERT INTO tsohaproject.additionaltrainings (training, description, active) VALUES ('LGBTQI', 'An overview of current LGBTQI themes in helpline contacts.', 'True');
INSERT INTO tsohaproject.additionaltrainings (training, description, active) VALUES ('Puberty and Sexuality', 'An update on information regarding puberty', 'True' );


INSERT INTO tsohaproject.tasks (task) VALUES ('child helpline phone');
INSERT INTO tsohaproject.tasks (task) VALUES ('child helpline chat');
INSERT INTO tsohaproject.tasks (task) VALUES ('parent helpline phone');
INSERT INTO tsohaproject.tasks (task) VALUES ('parent helpline chat');

INSERT INTO tsohaproject.activitylevel (level) VALUES ('break');
INSERT INTO tsohaproject.activitylevel (level) VALUES ('one');
INSERT INTO tsohaproject.activitylevel (level) VALUES ('two');

/* This is used to create demo-users for the application */

INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, startdate, basictraining, isactive) VALUES ('volunteer', 'Doe', 'John', 'johndoe','johndoe@doe.com', '+1-50-4565465','11-11-2021', '11-11-2021', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, startdate, basictraining, isactive) VALUES ('volunteer', 'Mustard', 'Roger', 'rogemus','rogermust@doe.com', '+1-54-44215325','12-7-2021', '11-11-2020', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, startdate, basictraining, isactive) VALUES ('volunteer', 'Avery', 'Ada', 'adaave','adavery@very.com', '+1-40-3123285','11-10-2021', '10-11-2021', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, isactive) VALUES ('coordinator', 'Elper', 'Harry', 'harelpe','h.elper@org.com', '+1-30-3567285', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, isactive) VALUES ('admin', 'Chief', 'Master', 'maschie','john-117@org.com', '+1-30-3567285', true);


INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (1,1);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (1,2);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (2,3);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (2,4);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (3,1);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (3,3);

INSERT INTO tsohaproject.currentactivity (user_id, activity_id, level_date) VALUES (1,3,'11-11-2021');
INSERT INTO tsohaproject.currentactivity (user_id, activity_id, level_date) VALUES (2,3,'12-7-2021');