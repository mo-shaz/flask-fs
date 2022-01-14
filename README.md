# Flask Full-Stack App
## Instructions to run locally

* Clone the repository:

        git clone [repo-name]

* Install additional packages(use a virtual-env to avoid global install):

        pip install -r requirements.txt

* Add environement variables for the database credentials. This can be done either in a <code>.env</code> file or by exporting them into your current terminal instance:

        export db_name=[your-db-name]
        export db_user=[your-db-username]
        export db_pass=[your-db-password]

* Run the server in development/debug mode:

        FLASK_APP=app.py FLASK_ENV=development flask run


* [Additional Feature] You can actually send a real email to the attendee confirming their registration. This can be done using the MailJet service. Just add the required credentials to your environment to activate this feature:

        export mailjet_email=[your-mailjet-email]
        export mailjet_key=[your-mailjet-api-key]
        export mailjet_secret=[your-mailjet-secret]

* If you'd like to test this feature out and don't have a MailJet account, check the project environment for the heroku-hosted (https://flask-full-stack.herokuapp.com/) link and test it out.
