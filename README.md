# volunteer-management-application
## SUMMARY
The purpose of this application is to provide a demonstration of a HR-type management system tailored for the needs of volunteer activities. This application was built as a course project and is meant for educational purposes only. To get the best demo-experience please read through the features before testing the demo-application.

**Web-version at Heroku:**

https://helpline-management.herokuapp.com/

## GENERAL
The demonstration setting is a fictional helpline service that provides counseling services for youth via digital platforms. Helpline contacts are answered by volunteer counselors who work under the supervision of a helpline team. The helpline team provides the volunteers a basic training for the task, additional trainings to update and enhance skills and tools required to carry out the helpline tasks. Volunteers are provided with additional support in the form of written feedback for the activities they have carried out. 

The helpline staff needs to store information on the volunteer workers to maintain the helpline activities. The basic principle is to store only information that is necessary and relevant for the helpline activity. A detailed list of information can be found in the file schema. Because the nature of this project is educational, some information requiring the storing of more sensitive content has been opted out to make sure that not in any point of development and testing such information would be submitted into this application and stored in its database (for instance a background check done to volunteers working with children and adolescents). Additionally because of the scope of the course the focus is on the most relevant basic features. 

## FEATURES
This application is tailored for demonstration purposes and carries out the purpose of being a proof-of-work. Idea is that basic features can be demonstrated with it and a final product is then tailored based on the requirement specifications of the buyer. In this demo users can try out the following features:

 - User can create an admin account
 - As an admin user can then
   - create user accounts in different roles
   - view and edit account information on users with role 'volunteer' and 'coordinator'
   - loan equipment to volunteers or mark additional trainings as completed
   - read and reply to activity reports
   - add new equipment that can be loaned to volunteers
   - add new additional training modules that volunteers can take
   - view simple reports on the application data
   - edit their personal information and change their password
- User can login with a role 'coordinator' account they have created. Role 'coordinator' accounts can
   - create user accounts with role volunteer (not with role coordinator or admin)
   - view and edit account information on users with role 'volunteer' (not with role coordinator)
   - loan equipment to volunteers or mark additional trainings as completed
   - read and reply to activity reports
   - add new equipment that can be loaned to volunteers
   - add new additional training modules that volunteers can take
   - edit their personal information and change their password
- User can login with a role 'volunteer' account they have created. Role 'volunteer' accounts can
  - Report activities they have carried out. Reports include
    - date the activity was carried out
    - what task the activity was related to
    - title
    - content
    - a checkbox for requesting feedback on the task carried out
  - View and edit their personal information
- All logged in users can also logout
- All users (whether or not they are logged in) can view the short page 'about us' and leave feedback on the application.


## TECHNICAL OVERVIEW

 - An up to date of user techonologies can be found from the requirements.txt. 
 - With schema.sql you can quickly create a copy of the database schema
 - Documentation/demodata.sql contains data that you can use to populate the database. Note that user accounts created this way do not have a password.
 - Documentation/activity-report-examples.txt contains a few examples to submit as activity reports

## PROJECT DOCUMENTATION

 - Documentation/project-documentation.md: A detailed description of the project phases
 - Documentation/useful-commands.txt: A few useful commands for a inexperienced programmer such as myself to use with the project.
 - Documentation/query_examples.sql: Examples of queries used in the application. Can be tested out a local copy of the project database.
 - Documentation/Project_plan_v1.pdf: The original concept for the project
 - Documentation/Database_diagram_v1.pdf: The original database concept. Can be compared to the final schema.sql
