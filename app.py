import os
import psycopg
from flask import Flask, request, redirect, url_for
from markupsafe import escape

# Functon that constructs an URL for the DB. 
# App can run in 2 modes - production or development. This is determinted by the 'APP_ENV' environment variable.

def get_database_url():
    if os.environ.get("APP_ENV") == "PRODUCTION":
        user = os.environ.get("POSTGRES_USER")
        password = os.environ.get("POSTGRES_PASSWORD")
        host = os.environ.get("POSTGRES_HOST")
        db = os.environ.get("POSTGRES_DB", "postgres")
        return f"postgresql://{user}:{password}@{host}:5432/{db}"
    elif os.environ.get("APP_ENV") == "DOCKER_DEV":
        return "postgres://postgres@host.docker.internal:5432/postgres" # This URL is for our local DB - if you see a connection error, you may need to edit this URL
    else:
        return "postgres://postgres@localhost:5432/postgres" # This URL is for our local DB - if you see a connection error, you may need to edit this URL
    
# Function sets up the DB with the right table

def setup_database(url):

    # Connect using the URL
    connection = psycopg.connect(url)

    # Get a 'cursor' object that we can use to run SQL
    cursor = connection.cursor()

    # Execute some SQL to create the table
    cursor.execute("CREATE TABLE IF NOT EXISTS messages (message TEXT);")

    # And commit the changes to ensure that they 'stick' in the DB
    connection.commit()

# We run the two functions above:
POSTGRES_URL = get_database_url()
setup_database(POSTGRES_URL)

app = Flask(__name__)

# GET route

@app.route("/")
def get_messages():
    connection = psycopg.connect(POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages;")
    rows = cursor.fetchall()
    return "<h2>Your Messages</h2>" + format_messages(rows) + generate_form()

def format_messages(messages):
    output = "<ul>"
    for message in messages:
        escaped_message = escape(message[0]) # We escape the message to avoid the user sending us HTML & tricking us into rendering it
        output += f"<li>{escaped_message}</li>"
    output += "</ul>"
    return output

def generate_form():
    return """
    <form action="/" method="POST">
        <input type="text" name="message">
        <input type="submit" value="Send">
    </form>
    """

# POST route

@app.route("/", methods=['POST'])
def post_message():
    message = request.form["message"]

    connection = psycopg.connect(POSTGRES_URL)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO messages (message) VALUES (%s);", (message,))
    connection.commit()

    return redirect(url_for("get_messages"))

# We also run the server differently depending on the environment
# In production we don't want the fancy error messages - users won't know what to do with them, so no 'debug=TRUE'

if __name__ == '__main__':
    if os.environ.get("APP_ENV") == "PRODUCTION":
        app.run(port=5002, host='0.0.0.0')
    else:
        app.run(debug=True, port=5002, host='0.0.0.0')

