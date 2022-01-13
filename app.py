# Package imports
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
import psycopg2



#####################################
#               CONFIG              #
#####################################

# ONLY IN DEVELOPMENT
if 'PRODUCTION' not in os.environ:
    load_dotenv()

# Instanitate the app
app = Flask(__name__)


# Database Config
db_name = os.environ['db_name']
db_user = os.environ['db_user']
db_pass = os.environ['db_pass']


# Function used to make the database connection
def connect_db():

        connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass)
        return connection


# Connect to the database and create a table
try:
    # Connect and get a cursor
    connection = connect_db()
    cursor = connection.cursor()

    # Construct the query
    create_table_query =  """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_name text NOT NULL,
            email text NOT NULL
            );"""

    # Execute and commit the query
    cursor.execute(create_table_query)
    connection.commit()

    # Close the connection
    cursor.close()
    connection.close()

except Exception as e:
    app.logger.error("Error creating table")
    app.logger.error(e)



#####################################
#               ROUTES              #
#####################################

# Home page
@app.route('/')
def home():

    return 'home_page'


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():

    # Show different responses for GET and POST
    if request.method == 'POST':

        # Get the form data
        email = request.form.get('email')
        username = request.form.get('username')

        # If form data is empty, return error
        if email == None or username == None:
            return 'fields are empty', 400
    
        # Check if the user already exists
        # We can do that by checking the email as emails are unique
        try:

            # Connect to the database
            connection = connect_db()
            cursor = connection.cursor()

            # Check for the email
            check_user_query = "SELECT * FROM users WHERE email=(%s);"
            cursor.execute(check_user_query, (email,))
            result = cursor.fetchone()

            # If no user, add the user
            if result == None:
                add_user_query = "INSERT INTO users(user_name, email) VALUES(%s, %s);"
                cursor.execute(add_user_query, (username, email))
                connection.commit()

                # Close the connection
                cursor.close()
                connection.close()

                # return response
                return 'user registered', 201

            else:
                # Close the connections and return error
                cursor.close()
                connection.close()

                return 'user already registered', 400


        except Exception as e:
            app.logger.error('Error registering user')
            app.logger.error(e)

            return 'INTERNAL SERVER ERROR', 500

    

    # If it is a GET request
    else:
        return 'register page'


# Attendees page
@app.route('/attendees')
def attendees():

    # Get the list of users from database
    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor()

        # Get all the users
        get_user_query = "SELECT user_name FROM users;"
        cursor.execute(get_user_query)
        result = cursor.fetchall()

        # Close the connection and return the result
        cursor.close()
        connection.close()

        return 'OK', 200

    except Exception as e:
        app.logger.error('Error getting users')
        app.logger.error(e)

        return 'INTERNAL SERVER ERROR', 500

