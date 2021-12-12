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

INSERT INTO tsohaproject.activitylevel (level) VALUES ('quit');
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

INSERT INTO tsohaproject.currentactivity (user_id, activity_id, level_date) VALUES (1,4,'11-11-2021');
INSERT INTO tsohaproject.currentactivity (user_id, activity_id, level_date) VALUES (2,4,'12-7-2021');

/* Some generic activities - volunteers */
Parent helpline:
It was a quiet night, only got a few calls. A mom of two young children called. She was exhausted. I did my best to listen and to encourage her to seek help.
A busy night at the parent helpline. Answerred multiple chat contacts. Most memorable one was from a father who wanted to know, how to react to his son coming out to him. 
A very quiet night at the parent helpline. Got no calls today.
Got three calls. A mother who regretted becoming a mother called. She felt that she was unable to provide the kind of life she wanted to her children. She had not talked with her spouse about her feelings. The other calls were about coping with babies (feeding, sleeping etc.)
A father of a young woman called. His daughter had moved to her own apartment and the father was worried about her life. She studied at the university, but the father was concerned that she wasn't performing well and that she could have some coping issues in life as well.'

Child helpline:
Busy evening in the chat. Most contacts dealt with anxiety and depressive thoughts.
Busy afternoon in the phone. Most callers were elementary aged children. Most had nothing particular they wished to talked about and just wanted someone to be with them for a while and to listen. 
I spoke with a 15-17 year old girl for three hours. She had been going through a rough time in her life. Her parents had divorced and she felt pressure to tip toe in order to not make either parent feel like she was favoring the other. 

/* Some generic replies - coordinators */
Wow, sounds like you had quite a challenging evening. Call me if you want to talk about it. Thanks for all your hard work!
Thanks for all your hard work! We really appreciate it. 
Keep up the good work! 


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


/* select users and count number of activities for each user */
SELECT user_id, (SELECT COUNT(*) FROM tsohaproject.messages LEFT JOIN tsohaproject.users ON (messages.volunteer_id = users.user_id) GROUP BY users.user_id) FROM tsohaproject.users;

SELECT users.*, COUNT(messages.volunteer_id) AS activitycounter FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.volunteer_id) WHERE role='volunteer' GROUP BY users.user_id;

/* Testing returning True/False based on whether volunteer has a certain qualification. In Postgres this is done with a CASE WHEN... THEN.... END */
SELECT tasks.task, tasks.task_id, CASE WHEN tasks.task_id IN (SELECT tasks.task_id FROM tsohaproject.users LEFT JOIN tsohaproject.volunteerqualification ON (users.user_id = volunteerqualification.user_id) LEFT JOIN tsohaproject.tasks ON (volunteerqualification.task_id = tasks.task_id) WHERE users.user_id = 9) THEN true ELSE false END AS isqualified FROM tsohaproject.tasks;

/* Get all messages in order  version 1 */

SELECT messages.msg_id, messages.activity_date, messages.content, tasks.task, users.lastname, users.firstname 
FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.volunteer_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
ORDER BY messages.activity_date DESC

/* Get all messages in order - versio 2 (problem: version 1 shows users with no messages) */

SELECT messages.msg_id, messages.activity_date, messages.content, tasks.task, users.role, users.lastname, users.firstname 
FROM tsohaproject.users INNER JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
ORDER BY messages.thread_id DESC, messages.activity_date DESC

/* Option two thanks to a friendly tip on Telegram :) */
SELECT messages.msg_id, messages.activity_date, messages.content, tasks.task, users.lastname, users.firstname 
FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.volunteer_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
WHERE messages.content IS NOT NULL
ORDER BY messages.activity_date DESC

/* To run Flask in development server mode */
export FLASK_ENV=development && flask run
postgres
psql


/* Fixed message query */
SELECT messages.msg_id, messages.thread_id, messages.activity_date, messages.send_date, messages.content, tasks.task, users.username, users.role, users.lastname, users.firstname 
            FROM tsohaproject.users INNER JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) 
            LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
            ORDER BY  messages.activity_date DESC, messages.thread_id DESC, messages.msg_id ASC;


/* Fixed query for receiving password */

SELECT users.user_id, users.role, password.password 
                FROM tsohaproject.users INNER JOIN tsohaproject.password ON users.user_id = password.user_id
                WHERE users.username='majuriperuna'

/* Exploring getting most recent value. */
/* This works as intented */
SELECT user_id, MAX(level_date) FROM tsohaproject.currentactivity WHERE user_id=7 GROUP BY user_id;
/* This does not yet work */
SELECT user_id, activity_id, MAX(level_date)  FROM tsohaproject.currentactivity LEFT JOIN tsohaproject.activitylevel ON currentactivity.activity_id = activitylevel.activity_id WHERE user_id=7 GROUP BY user_id;

/* Workaround */
SELECT currentactivity.user_id, currentactivity.level_date, activitylevel.level FROM tsohaproject.currentactivity LEFT JOIN tsohaproject.activitylevel ON (currentactivity.activity_id = activitylevel.activity_id) WHERE user_id = 7 ORDER BY level_date DESC LIMIT 1; 


/* Get additional trainings */

SELECT additionaltrainings.training, trainingparticipation.training_date FROM tsohaproject.trainingparticipation LEFT JOIN tsohaproject.additionaltrainings ON (trainingparticipation.training_id = additionaltrainings.training_id) WHERE user_id = 7 ORDER BY training_date DESC; 

/* Get loaned tools */
SELECT loanedtools.loandate, tools.tool, tools.serialnumber FROM tsohaproject.loanedtools LEFT JOIN tsohaproject.tools ON (loanedtools.tool_id = tools.tool_id) WHERE user_id = 7 AND loanedtools.loaned = true;


/* Deleted from the app */
SELECT users.lastname, users.role, users.firstname, users.user_id, users.email, string_agg(tasks.task, ', ') FROM tsohaproject.users, tsohaproject.volunteerqualification, tsohaproject.tasks WHERE users.user_id = volunteerqualification.user_id AND tasks.task_id = volunteerqualification.task_id GROUP BY users.lastname, users.firstname, users.role, users.user_id, users.email;


/* Search query */
SELECT user_id, lastname, firstname, email FROM (SELECT user_id, lastname, firstname, email, lastname || ' ' || firstname || ' ' || username || ' ' || email AS document  FROM tsohaproject.users WHERE role='volunteer') as subset WHERE document LIKE '%:query%';


/* Combine search query to volunteer-query */

SELECT users.user_id, users.role, users.lastname, users.firstname, users.username, users.email, users.phone, startdate, COUNT(messages.sender_id) AS activitycounter 
FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) LEFT JOIN (SELECT user_id, lastname || ' ' || firstname || ' ' || username || ' ' || email AS document  FROM tsohaproject.users WHERE role='volunteer') as subset ON (messages.sender_id = subset.user_id)
WHERE role='volunteer' AND isactive='true' AND document LIKE '%:query%'
GROUP BY users.user_id


SELECT users.user_id, users.role, users.lastname, users.firstname, users.username, users.email, startdate, COUNT(messages.sender_id) AS activitycounter 
FROM (SELECT user_id, lastname || ' ' || firstname || ' ' || username || ' ' || email AS document  FROM tsohaproject.users WHERE role='volunteer') AS subset LEFT JOIN tsohaproject.users ON (subset.user_id = users.user_id) LEFT JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) 
WHERE role='volunteer' AND isactive='true' AND LOWER(document) LIKE LOWER('%jes%')
GROUP BY users.user_id;

SELECT messages.thread_id, messages.msg_id, messages.activity_date, messages.send_date, messages.content, tasks.task, users.username, users.role, users.lastname, users.firstname 
FROM tsohaproject.users INNER JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
ORDER BY messages.thread_id DESC, messages.activity_date ASC;

/* Searching users without a subquery */

SELECT users.user_id, users.role, users.lastname, users.firstname, users.username, users.email, users.phone, startdate, COUNT(messages.sender_id) AS activitycounter, user_id, lastname || ' ' || firstname || ' ' || email  AS document
FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) 
WHERE role='volunteer' AND isactive='true' AND (lastname || ' ' || firstname || ' ' || email) LIKE '%a%' 
GROUP BY users.user_id;

SELECT messages.activity_date, messages.content, tasks.task 
FROM tsohaproject.messages LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
WHERE messages.volunteer_id=7 
ORDER BY messages.activity_date DESC 
LIMIT 5 OFFSET 0

/* Testing out features of ORDER BY */
SELECT users.user_id, messages.activity_date, messages.content, tasks.task, thread_id, msg_id, sender_id 
FROM tsohaproject.users LEFT JOIN tsohaproject.messages ON users.user_id = messages.sender_id LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
WHERE messages.volunteer_id=7 
ORDER BY messages.activity_date DESC, messages.thread_id DESC, messages.msg_id ASC 
LIMIT 5 OFFSET 0;

SELECT messages.msg_id, messages.thread_id, messages.activity_date, messages.send_date, messages.content, tasks.task, users.username, users.role, users.lastname, users.firstname 
        FROM tsohaproject.users INNER JOIN tsohaproject.messages ON (users.user_id = messages.sender_id) LEFT JOIN tsohaproject.tasks ON (messages.task_id = tasks.task_id) 
        ORDER BY activity_date DESC, thread_id, msg_id ASC;





SELECT currentactivity.activity_id AS a_id, activitylevel.level AS level, MAX(currentactivity.level_date) AS a_date 
FROM tsohaproject.users LEFT JOIN tsohaproject.currentactivity ON users.user_id = currentactivity.user_id LEFT JOIN tsohaproject.activitylevel ON currentactivity.activity_id =activitylevel.activity_id 
WHERE users.user_id=7
GROUP BY a_id, level
