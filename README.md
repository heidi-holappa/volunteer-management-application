# volunteer-management-application
## SUMMARY
The purpose of this application is to provide a demonstration of a HR-type management system tailored for the needs of volunteer activities. This application was built as a course project and is meant for educational purposes only. 

## GENERAL
The demonstration setting is a fictional helpline service that provides counseling services for youth via digital platforms. Helpline contacts are answered by volunteer counselors who work under the supervision of a helpline team. The helpline team provides the volunteers a basic training for the task, additional training to update and enhance skills and tools required to carry out the helpline tasks. Volunteers are provided with additional support in the form of development discussions. 

The helpline staff needs to store information on the volunteer workers to maintain the helpline activities. The basic principle is to store only information that is necessary and relevant for the helpline activity. A detailed list of information is described later on. Because the nature of this project is educational, some information requiring the storing of more sensitive content has been opted out to make sure that not in any point of development and testing such information would be submitted into this application and stored in its database (for instance a background check done to volunteers working with children and adolescents). Additionally because of the scope of the course the focus is on the most relevant basic features. 

## PHASE 2
For easier reading experience you can view what's happening with the app in phase 2 from this section. To see the initial project plan from phase 1 please review sections Featuers and Datamodel. All feedback is very welcome. I would especially appreciate feedback on 'Missing features.' Is there something I have overlooked that I should add to the list?

**Web-version at Heroku:** The project is up and running in Heroku. You can find the project from 

https://helpline-management.herokuapp.com

**State of the project**
 - You can create an admin account and login into the application
 - You can sign in into the account
 - You can logout once logged in. 
 - The site has two pages that can be viewed without logging in. They are located in the footer (About us, Feedback). If user is logged in, these pages have a button to logout. Otherwise these pages have a button for logging in. Please note that as of now the feedback form does not actually submit feedback. That function is still to be built. 
 - As an admin you can create accounts for roles 'volunteer' and 'coordinator'
 - As an admin you can view created volunteers and view detailed information from a selected volunteer. Note: Editing volunteer information does not yet work. 
 - With an account with role 'volunteer' you can login into the volunteer view and post messages. 
 - As an admin you can view messages posted by volunteers. You can search messages based on content. 
 - Userlist shows how many tasks each volunteer user has carried out
 - Different pages have been initially authorized (only authorized users can view selected pages). Authorization needs to be improved.

**Missing features (to be built for phase 3)**
- Information validation: At the least it should be checked that all needed information is set. If not, user should receive an informative error message.
- Usability: Update instructive texts
- Messages can be replied by coordinators and admins
- Search functions for userlist
- Filters for userlist
- Admin can delete users (note: soft delete at this point. Users state is set to not active. In a real PROD-app personal information would be purged/pseudonymized, but all relevant information would be kept - activities performed, training-participations, loan history, etc.)
- Volunteer information can be edited. 
- Volunteers can be loaned tools, activity level can be changed and additional trainings can be added to their information. 
- Authorization is improved.
- The overall look of the user interface needs to be polished. Some initial accessibility testing should also be performed (can this site be used well in a text based browser for instance)

**If there is time, these'd be nice to add (but are not a top priority):**
- Some simple report data (training participations, performed activities per year and month)
- Some simple log-information (who has done and what)

**Other information:** If you wish to create a local version of the application, you can find demodata for the project in the file demodata.sql. The file also contains some queries you can test in psql to test out the project and for educational purposes. 

## FEATURES
This application can be used in different roles. Helpline coordinators manage personal information stored about volunteers. Coordinators also create accounts for volunteers. Volunteers use this application to report on volunteer activities they perform. Volunteers have an access to review what information has been stored about them. The application also has an administrator who has access to some additional features in the application (detailed below).  The helpline staff can send messages to a volunteer and a volunteer can send messages to the helpline staff. 

**1. Coordinators**
Coordinators manage personal information collected and stored about each volunteer. Coordinators can add new volunteers and update information on existing volunteers. Coordinators can send volunteers messages (detailed in part 4) and review all information available on each volunteer. Following information will be stored in the application on each volunteer. Items marked with * are mandatory, other items are optional. 
  - last name*
  - first name*
  - username*
  - email address*
  - phone number*
  - date volunteer career started*
  - date career ended
  - level of activity (two or more shifts month, one shift per month, on a leave, terminated)*
  - basic training (date graduated)*
  - additional trainings
  - tools provided (laptop, smartphone, headset)
  - development discussions held (date)

**2. Volunteers**
Volunteers can review information stored about them and volunteers can send messages to staff. Volunteers can submit tasks they have completed. A task includes a date, type of task and brief summary of activities performed. 
  - date (dd.mm.yyyy)
  - type of activity (chat-counselling / phone counselling / group chat supervisor)
  - summary of activity (open text field)

**3. Administrator**
Administrator can perform all the tasks a coordinator can perform. Additionally an administrator can add new types of training modules, new types of tools, new types of volunteer activities. An administrator can also create new coordinators
Optional: An administrator can also delete volunteers. Upon deletion a volunteer will be 
‘pseudonymized,’ meaning all personal information will me removed but all activitity will be kept intact. 

**4. Personal message**
A personal message can be sent to a volunteer through the application. Sent messages form a correspondence. The correspondence can be seen by the volunteer, all coordinators and all administrators. Message content:
  - timestamp (hh:mm dd.mm.yyyy)
  - message sender
  - message content

**5. Creating a new user**
Administrators can create new coordinators and volunteers. Coordinators can create new volunteers. For each created user a default password is set (I.e. password: changeme). Upon first login the password has to be reset. 

## DATAMODEL
This is an initial concept for the data model. The datatypes will be clarified later when the database solution has been familiarized with. 

**Table: Users**
Description: contains basic user information. All users are stored in the same table. The role defines what is the role for each user. 
  - user_id (PRIMARY ID KEY)
  - role (VARCHAR)
  - lastname (VARCHAR)
  - firstname (VARCHAR)
  - username (VARCHAR)
  - email (VARCHAR)
  - phone (VARCHAR)
  - startdate (DATE)
  - enddate (DATE)
  - basictraining (DATE)

**Table: Activitylevel**
Description: This table details the available activity levels. 
  - activity_id (PRIMARY ID KEY)
  - level [two or more shifts month, one shift per month, on a leave, terminated]

**Table: Currentactivity**
Description: this table stores all the instances in which the activity level for each volunteer has been set. This could be used in future to track how well each volunteer has committed to the mutually agreed upon activity level. That is beyond the scope of this project, but this solution creates a foundation for future additional development. 
  - date (DATE)
  - from table: Users: user_id
  - from table: Activitylevel: activity_id

**Table Tasks**
Description: This table contains the different tasks volunteers can participate in
  - task_id (PRIMARY ID KEY)
  - task (VARCHAR)

**Table Volunteerqualification**
Description: This table contains a list of tasks each volunteer has been approved to carry out. 
  - from table: Users: user_id
  - from table: Tasks: task_id

**Table: Volunteeraction**
Description: This table contains all the activities volunteers have carried out. 
  - from table: Users: user_id
  - from table: Tasks: task_id
  - date (DATE)
  - description (VARCHAR)

**Table: Additionaltrainings**
Description: This table details the additional training modules available to volunteers. 
  - training_id (PRIMARY ID KEY)
  - training (VARCHAR)

**Table: Tools**
Description: This table details the tools that can be loaned to volunteers.
  - tool_id (PRIMARY ID KEY)
  - tooltype (VARCHAR)
  - serialnumber (VARCHAR)
  - loaned (BOOLEAN)

**Table: Loanedtools**
Description: details the tools given to each volunteer
  - from table: Users: user_id
  - from table: Tools: tool_id
  - loandate (DATE)
  - returndate (DATE)
  - loaned (BOOLEAN)

**Table: Developmentdiscussion**
Description: The date, volunteer_id and coordinator_id are stored. 
  - date (DATE)
  - volunteer_id from table: Users: user_id
  - coordinator_id from table: Users: user_id

**Table: Messages**
Description: This table contains sent messages. Every row includes the message id, volunteer to whom the message is related to, sender id, timestamp and the message content.
  - msg_id (PRIMARY ID KEY)
  - volunteer_id (from Table Users: user_id)
  - sender_id (from Table Users: user_id)
  - timestamp (TIMESTAMP)
  - content (A DATATYPE THAT CAN HANDLE LONG STRINGS OF TEXT)

**Table: Password**
Description: This table contains encrypted versions of user passwords
  - from table: Users: user_id
  - password (VARCHAR)

**Table: log**
Description: Contains information on actions performed in the application. Description contains a description of the action carried out (i.e. updated field ‘email’).
  - user_id (from table: Users: user_id)
  - timestamp (TIMESTAMP)
  - description: (VARCHAR)

## Additional information
Please see the folder documentation for additional project information. At the moment the database schema and a diagram of the database model can be reviewed. 
