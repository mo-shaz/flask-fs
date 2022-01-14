# Package imports
import os
import sys
import re
from dotenv import load_dotenv
from flask import Flask, request, render_template
import psycopg2
from mailjet_rest import Client



#####################################
#               CONFIG              #
#####################################

# ONLY IN DEVELOPMENT
if 'PRODUCTION' not in os.environ:
    load_dotenv()

# Instanitate the app
app = Flask(__name__)


# Database Config
try:
    db_string = os.environ['DATABASE_URL']

except Exception as e:
    app.logger.error('Database configuration failed')
    app.logger.error(f"Key {e} not found")
    sys.exit(1)




#################################################
#               UTILITY FUNCTIONS               #
#################################################

# Function used to make the database connection
def connect_db():

        connection = psycopg2.connect(db_string)
        return connection


# Function to check the validity of emails
def is_valid(email):
    # The pattern
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email):
        return True

    else:
        return False

# Function to send email using the MailJet service
def send_mail(attendee_email):
    # Load the credentials
    api_key = os.environ['mailjet_key']
    api_secret = os.environ['mailjet_secret']
    sender_mail = os.environ['mailjet_email']

    # Initialize the transport
    transport = Client(auth=(api_key, api_secret), version='v3.1')

    # Construct the mail content
    data = {
            'Messages': [
                {
                    'From': {
                        'Email': sender_mail,
                        'Name': 'Baking Workshop'
                        },
                    'To': [
                        {
                            'Email': attendee_email,
                            'Name': 'Workshop Attendee'
                            }
                        ],
                    'Subject': 'Baking Workshop Invite',
                    'TextPart': 'Hello there Attendee, thanks for registering for the workshop. Hope to see you soon. Have a great day.',
                    'HTMLPart': '<h4>Hello there,</h4><p>thanks for registering for the workshop. Hope to see you soon.</p>'
                    }
                ]
            }

    # Send the mail
    response = transport.send.create(data=data)
    app.logger.info(f"mail_status_code: {response.status_code}")

    return


# Connect to the database and create a table
try:
    # Connect and get a cursor
    connection = connect_db()
    cursor = connection.cursor()

    # Construct the query
    create_table_query =  """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            user_name text NOT NULL,
            email text NOT NULL,
            reg_date date NOT NULL DEFAULT CURRENT_DATE
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
    sys.exit(1)



#####################################
#               ROUTES              #
#####################################

# Home page
@app.route('/')
def home():

    return render_template('home.html')


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():

    # Show different responses for GET and POST
    if request.method == 'POST':

        # Get the form data
        email = request.form.get('email') or None
        username = request.form.get('username') or None

        # If form data is empty, return error
        if email == None or username == None:
            return render_template('error.html', data='Error: fields are empty'), 400

        # An additional check for the validity of email
        if is_valid(email) == False:
            return render_template('error.html', data='Error: invalid email format'), 400
    
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

                ############################
                # SEND AN EMAIL (OPTIONAL) #
                ############################
                if 'mailjet_email' in os.environ and 'mailjet_key' in os.environ and 'mailjet_secret' in os.environ:
                    send_mail(email)

                # return response
                return render_template('success.html', data='Success: user registered'), 201

            else:
                # Close the connections and return error
                cursor.close()
                connection.close()

                return render_template('error.html', data='Error: user already registered'), 400


        except Exception as e:
            app.logger.error('Error registering user')
            app.logger.error(e)

            return render_template('error.html', data='INTERNAL SERVER ERROR'), 500

    

    # If it is a GET request
    else:
        return render_template('register.html') 


# Attendees page
@app.route('/attendees')
def attendees():

    # Get the list of users from database
    try:
        # Connect to the database
        connection = connect_db()
        cursor = connection.cursor()

        # Get all the users
        get_user_query = "SELECT user_name, reg_date FROM users;"
        cursor.execute(get_user_query)
        result = cursor.fetchall()

        # Close the connection and return the result
        cursor.close()
        connection.close()

        return render_template('attendees.html', data=result), 200

    except Exception as e:
        app.logger.error('Error getting users')
        app.logger.error(e)

        return render_template('error.html', data='INTERNAL SERVER ERROR'), 500

