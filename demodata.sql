/* This is used to create demo-data for the application */

INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '1234-12345678', false);
INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '2234-12345678', false);
INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '3234-12345678', false);
INSERT INTO tsohaproject.tools (tool, serialnumber, loaned) VALUES ('Nokia 3310', '4234-12345678', false);

INSERT INTO tsohaproject.additionaltrainings (training) VALUES ('mental health');
INSERT INTO tsohaproject.additionaltrainings (training) VALUES ('LGBTQI');
INSERT INTO tsohaproject.additionaltrainings (training) VALUES ('Puberty and sexuality');


INSERT INTO tsohaproject.tasks (task) VALUES ('child helpline phone');
INSERT INTO tsohaproject.tasks (task) VALUES ('child helpline chat');
INSERT INTO tsohaproject.tasks (task) VALUES ('parent helpline phone');
INSERT INTO tsohaproject.tasks (task) VALUES ('parent helpline chat');

INSERT INTO tsohaproject.activitylevel (level) VALUES ('quit');
INSERT INTO tsohaproject.activitylevel (level) VALUES ('break');
INSERT INTO tsohaproject.activitylevel (level) VALUES ('one');
INSERT INTO tsohaproject.activitylevel (level) VALUES ('two');

/* This is used to create demo-users for the application */

INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, startdate, basictraining, isactive) VALUES ('volunteer', 'Doe', 'John', 'johndoe','johndoe@doe.com', '+1-50-4565465','11-11-2021', '11-11-2021', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, startdate, basictraining, isactive) VALUES ('volunteer', 'Mustard', 'Roger', 'rogemus','rogermust@doe.com', '+1-54-44215325','12-7-2021', '21-11-2020', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, startdate, basictraining, isactive) VALUES ('volunteer', 'Avery', 'Ada', 'adaave','adavery@very.com', '+1-40-3123285','11-10-2021', '10-11-2021', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, isactive) VALUES ('coordinator', 'Elper', 'Harry', 'harelpe','h.elper@org.com', '+1-30-3567285', true);
INSERT INTO tsohaproject.users (role, lastname, firstname, username, email, phone, isactive) VALUES ('admin', 'Chief', 'Master', 'maschie','john-117@org.com', '+1-30-3567285', true);


INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (1,1);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (1,2);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (2,3);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (2,4);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (3,1);
INSERT INTO tsohaproject.volunteerqualification (user_id, task_id) VALUES (3,3);

INSERT INTO tsohaproject.currentactivity (user_id, activity_id, level_date) VALUES (1,4,'11-11-2021');
INSERT INTO tsohaproject.currentactivity (user_id, activity_id, level_date) VALUES (2,4,'12-7-2021');





/* To delete the tsohaproject from database: */
DROP SCHEMA IF EXISTS tsohaproject CASCADE;

/* Add strings as a list. NOTE: only works on strings */

SELECT users.lastname, users.firstname, string_agg(tasks.task, ', ')
FROM tsohaproject.users, tsohaproject.volunteerqualification, tsohaproject.tasks
WHERE users.user_id = volunteerqualification.user_id AND tasks.task_id = volunteerqualification.task_id
GROUP BY users.lastname, users.firstname;

SELECT users.lastname, users.role, users.firstname, users.user_id, users.email, string_agg(tasks.task, ', ')
FROM tsohaproject.users, tsohaproject.volunteerqualification, tsohaproject.tasks
WHERE users.user_id = volunteerqualification.user_id AND tasks.task_id = volunteerqualification.task_id
GROUP BY users.lastname, users.firstname, users.role, users.user_id, users.email;

SELECT string_agg(task_id, ',')
FROM tsohaproject.volunteerqualification
GROUP BY user_id;

/* Herokuapp URL  */
https://helpline-management.herokuapp.com/ | https://git.heroku.com/helpline-management.git

/*Testing different ways to use returning*/
with rows as (INSERT INTO tsohaproject.users (username, role, isactive) VALUES ('peruna', 'admin', TRUE) RETURNING user_id)
INSERT INTO tsohaproject.password (password, user_id) VALUES ('salasana', (SELECT user_id FROM rows);
INSERT INTO tsohaproject.password (password, user_id) VALUES ('salasana', (INSERT INTO tsohaproject.users (username, role, isactive) VALUES ('peruna', 'admin', TRUE) RETURNING user_id));

/* For testing LEFT JOIN with the demo data */
SELECT tasks.task  FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON users.user_id = volunteerqualification.user_id LEFT JOIN tsohaproject.tasks on volunteerqualification.task_id = tasks.task_id WHERE users.user_id = 3;
SELECT activitylevel.level, currentactivity.date  FROM tsohaproject.users LEFT JOIN tsohaproject.currentactivity ON users.user_id = currentactivity.user_id LEFT JOIN tsohaproject.activitylevel on currentactivity.activity_id = activitylevel.activity_id WHERE users.user_id=3;


/* Testing returning True/False based on whether volunteer has a certain qualification. In Postgres this is done with a CASE WHEN... THEN.... END */


SELECT tasks.task, tasks.task_id, CASE WHEN tasks.task_id IN (SELECT tasks.task_id FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON (users.user_id = volunteerqualification.user_id) LEFT JOIN tsohaproject.tasks ON (volunteerqualification.task_id = tasks.task_id) WHERE users.user_id = 9) THEN true ELSE false END AS isqualified FROM tsohaproject.tasks;

/* Get all messages in order */

SELECT messages.msg_id, messages.activity_date, messages.content, tasks.task, users.lastname, users.firstname FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.volunteer_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) ORDER BY messages.activity_date DESC

/* To run Flask in development server mode */
export FLASK_ENV=development && flask run

