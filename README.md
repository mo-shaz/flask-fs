# Flask Full-Stack App
## Instructions to run locally

* Clone the repository:
        git clone [repo-name]

* Add environement variables for the database credentials. This can be done either in a <code>.env</code> file or by exporting them into your current terminal instance:
        export db_name=[your-db-name]
        export db_user=[your-db-username]
        export db_pass=[your-db-password]

* Run the server in development/debug mode:
        FLASK_APP=app.py FLASK_ENV=development flask run
