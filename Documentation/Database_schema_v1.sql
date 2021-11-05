CREATE TABLE "Users" (
  "user_id" integer PRIMARY KEY,
  "role" varchar,
  "lastname" varchar,
  "firstname" varchar,
  "username" varchar,
  "email" varchar,
  "phone" varchar,
  "startdate" date,
  "enddate" date,
  "basictraining" date
);

CREATE TABLE "Activitylevel" (
  "activity_id" integer PRIMARY KEY,
  "level" varchar
);

CREATE TABLE "Currentactivity" (
  "date" date,
  "user_id" integer,
  "acitivy_id" interget
);

CREATE TABLE "Additionaltrainings" (
  "training_id" integer PRIMARY KEY,
  "training" varchar
);

CREATE TABLE "Tasks" (
  "task_id" integer PRIMARY KEY,
  "task" varchar
);

CREATE TABLE "Volunteerqualification" (
  "user_id" integer,
  "task_id" integer
);

CREATE TABLE "Volunteeraction" (
  "user_id" integer,
  "task_id" integer,
  "date" date,
  "description" varchar
);

CREATE TABLE "Tools" (
  "tool_id" integer PRIMARY KEY,
  "tool" varchar,
  "serialnumber" varchar,
  "loaned" boolean
);

CREATE TABLE "Loanedtools" (
  "user_id" integer,
  "tool_id" integer,
  "loandate" date,
  "returndate" date,
  "loaned" boolean
);

CREATE TABLE "Developmentdiscussion" (
  "date" date,
  "volunteer_id" integer,
  "coordinator_id" integer
);

CREATE TABLE "Messages" (
  "msg_id" integer PRIMARY KEY,
  "volunteer_id" integer,
  "sender_id" integer,
  "timestamp" timestamp,
  "content" blob
);

CREATE TABLE "password" (
  "user_id" integer,
  "password" varchar
);

CREATE TABLE "Log" (
  "user_id" integer,
  "timestamp" timestamp,
  "description" varchar
);

ALTER TABLE "Currentactivity" ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Currentactivity" ADD FOREIGN KEY ("acitivy_id") REFERENCES "Activitylevel" ("activity_id");

ALTER TABLE "Volunteerqualification" ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Volunteerqualification" ADD FOREIGN KEY ("task_id") REFERENCES "Tasks" ("task_id");

ALTER TABLE "Volunteeraction" ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Volunteeraction" ADD FOREIGN KEY ("task_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Loanedtools" ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Loanedtools" ADD FOREIGN KEY ("tool_id") REFERENCES "Tools" ("tool_id");

ALTER TABLE "Developmentdiscussion" ADD FOREIGN KEY ("volunteer_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Developmentdiscussion" ADD FOREIGN KEY ("coordinator_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Messages" ADD FOREIGN KEY ("volunteer_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Messages" ADD FOREIGN KEY ("sender_id") REFERENCES "Users" ("user_id");

ALTER TABLE "password" ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("user_id");

ALTER TABLE "Log" ADD FOREIGN KEY ("user_id") REFERENCES "Users" ("user_id");
