CREATE SCHEMA tsohaproject;

CREATE TABLE "tsohaproject".USERS (
  "user_id" SERIAL PRIMARY KEY,
  "role" varchar,
  "lastname" varchar,
  "firstname" varchar,
  "username" varchar UNIQUE,
  "email" varchar,
  "phone" varchar,
  "startdate" date,
  "enddate" date,
  "basictraining" date,
  "isactive" boolean
);

CREATE TABLE "tsohaproject".ACTIVITYLEVEL (
  "activity_id" SERIAL PRIMARY KEY,
  "level" varchar
);

CREATE TABLE "tsohaproject".CURRENTACTIVITY (
  "level_date" date,
  "user_id" integer,
  "activity_id" integer
);

CREATE TABLE "tsohaproject".ADDITIONALTRAININGS (
  "training_id" SERIAL PRIMARY KEY,
  "training" varchar
);

CREATE TABLE "tsohaproject".TRAININGPARTICIPATION (
  "training_id" integer,
  "user_id" integer,
  "training_date" date
);

CREATE TABLE "tsohaproject".TASKS (
  "task_id" SERIAL PRIMARY KEY,
  "task" varchar
);

CREATE TABLE "tsohaproject".VOLUNTEERQUALIFICATION (
  "user_id" integer,
  "task_id" integer
);

CREATE TABLE "tsohaproject".VOLUNTEERACTION (
  "user_id" integer,
  "task_id" integer,
  "date" date,
  "description" varchar
);

CREATE TABLE "tsohaproject".TOOLS (
  "tool_id" SERIAL PRIMARY KEY,
  "tool" varchar,
  "serialnumber" varchar,
  "loaned" boolean
);

CREATE TABLE "tsohaproject".LOANEDTOOLS (
  "user_id" integer,
  "tool_id" integer,
  "loandate" date,
  "returndate" date,
  "loaned" boolean
);

CREATE TABLE "tsohaproject".DEVELOPMENTDISCUSSION (
  "discussion_date" date,
  "volunteer_id" integer,
  "coordinator_id" integer
);

CREATE TABLE "tsohaproject".MESSAGES (
  "msg_id" SERIAL PRIMARY KEY,
  "thread_id" integer,
  "sender_id" integer,
  "volunteer_id" integer,
  "task_id" integer,
  "activity_date" date,
  "send_date" timestamp,
  "content" varchar
);

CREATE TABLE "tsohaproject".PASSWORD (
  "user_id" integer,
  "password" varchar
);

CREATE TABLE "tsohaproject".APPLOG (
  "user_id" integer,
  "timestamp" timestamp,
  "description" varchar
);

CREATE TABLE "tsohaproject".FEEDBACK (
  "feedback_date" date,
  "content" varchar
);

ALTER TABLE "tsohaproject".CURRENTACTIVITY ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".CURRENTACTIVITY ADD FOREIGN KEY ("activity_id") REFERENCES "tsohaproject".ACTIVITYLEVEL ("activity_id");

ALTER TABLE "tsohaproject".VOLUNTEERQUALIFICATION ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".VOLUNTEERQUALIFICATION ADD FOREIGN KEY ("task_id") REFERENCES "tsohaproject".TASKS ("task_id");

ALTER TABLE "tsohaproject".VOLUNTEERACTION ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".VOLUNTEERACTION ADD FOREIGN KEY ("task_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".LOANEDTOOLS ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".LOANEDTOOLS ADD FOREIGN KEY ("tool_id") REFERENCES "tsohaproject".TOOLS ("tool_id");

ALTER TABLE "tsohaproject".TRAININGPARTICIPATION ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".TRAININGPARTICIPATION ADD FOREIGN KEY ("training_id") REFERENCES "tsohaproject".ADDITIONALTRAININGS ("training_id");

ALTER TABLE "tsohaproject".DEVELOPMENTDISCUSSION ADD FOREIGN KEY ("volunteer_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".DEVELOPMENTDISCUSSION ADD FOREIGN KEY ("coordinator_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".MESSAGES ADD FOREIGN KEY ("volunteer_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".MESSAGES ADD FOREIGN KEY ("sender_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".PASSWORD ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".APPLOG ADD FOREIGN KEY ("user_id") REFERENCES "tsohaproject".USERS ("user_id");

ALTER TABLE "tsohaproject".MESSAGES ADD FOREIGN KEY ("task_id") REFERENCES "tsohaproject".tasks ("task_id");
