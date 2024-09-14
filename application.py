from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_session import Session
from flask_googlemaps import GoogleMaps
import requests
import json
import boto3

application = Flask(__name__)
application.secret_key = 'secret key' 

# session configuration
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem' 
Session(application)

# Google Maps API key
application.config['GOOGLEMAPS_KEY'] = ""
GoogleMaps(application)

@application.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = api_login(email, password)
        if user:
            save_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@application.route('/logout')
def logout():
    clear_user()
    return redirect(url_for('home'))

@application.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user
    """
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        user_type = request.form['user-type']

        # save user to database
        response = api_register(email, name, phone, password, user_type)

        if response == 'User already exists':
            flash('User already exists', 'error')
            return redirect(url_for('register'))
        elif response == 'Error: Something went wrong':
            flash('Something went wrong', 'error')
            return redirect(url_for('register'))

        # save user to session
        user = {
            'email': email,
            'name': name,
            'phone': phone,
            'type': user_type
        }
        save_user(user)

        return redirect(url_for('home'))
    
    return render_template('register.html')

@application.route('/create-rides', methods=['GET', 'POST'])
def create_rides():
    """
    Create a new ride offer
    """
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']
        time = request.form['time']
        seats = request.form['seats']

        # save ride to database
        # ...

        return redirect(url_for('home'))
    return render_template('create_rides.html')

@application.route('/manage-rides', methods=['GET', 'POST'])
def manage_rides():
    """
    Manage ride offers
    """
    # get all rides from database
    rides = []
    return render_template('manage_rides.html', rides=rides)

@application.route('/search-rides', methods=['GET', 'POST'])
def search_rides():
    """
    Search for ride offers
    """
    print('In search rides')
    if request.method == 'POST':
        print('In post')
        origin = request.form.get('from')
        destination = request.form.get('to')

        print(f"origin: {origin}")
        print(f"destination: {destination}")
        # origin = request.form['origin']
        # destination = request.form['destination']
        # date = request.form['date']

        # search for rides in database
        # return render_template('search_rides.html', rides=rides)
    return render_template('maps.html')
    

### API functions ###

# call user API that triggers login lambda function
def api_login(email: str, password: str) -> dict:
    query_string = f'email={email}&password={password}'
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/user/login?' + query_string
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return (response.json())[0]
    else:
        if response.status_code == 404:
            return None
        return 'Error: Something went wrong'
    
# call user API that triggers register lambda function
def api_register(email: str, name: str, phone: int, password: str, user_type: str) -> dict:
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/user/register?'
    body = {
        'email': email,
        'name': name,
        'phone': phone,
        'password': password,
        'type': user_type
    }
    response = requests.post(api_url, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        if response.status_code == 404:
            return response.json()['message']
        return 'Error: Something went wrong'

### session functions ###
def is_logged_in() -> bool:
    return 'email' in session

def save_user(user: dict) -> None:
    session['email'] = user['email']
    session['name'] = user['name']
    session['type'] = user['type']

def clear_user() -> None:
    session.pop('email', None)
    session.pop('name', None)
    session.pop('type', None)


if __name__ == '__main__':
    application.run(debug=True)