from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_session import Session
from datetime import datetime
import requests
import json

application = Flask(__name__)
application.secret_key = 'secret key' 

# session configuration
application.config['SESSION_PERMANENT'] = False
application.config['SESSION_TYPE'] = 'filesystem' 
Session(application)

@application.route('/', methods=['GET', 'POST'])
def home():
    # check if user is logged in
    if is_logged_in() and session['type'] == 'driver':
        driver_id = session['email']
        if check_driver_rides(driver_id):
            rides = get_driver_rides(driver_id)
        else:
            rides = api_get_all_driver_rides(driver_id)
            if rides == 'Error: Something went wrong':
                rides = None
            save_driver_rides(driver_id, rides)
    elif is_logged_in() and session['type'] == 'passenger':
        if check_rides():
            rides = get_all_rides()
        else:
            rides = api_get_all_rides()
            save_rides(rides)

    return render_template('index.html')

@application.route('/login', methods=['GET', 'POST'])
def login():  
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
    session.pop('rides', None)
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
        vehicle = request.form['vehicle']
        license_plate = request.form['license-plate']

        # save user to database
        response = api_register(email, name, phone, password, user_type, vehicle, license_plate)

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

        return redirect(url_for('login'))
    
    return render_template('register.html')

@application.route('/rides/create', methods=['GET', 'POST'])
def create_rides():
    """
    Create a new ride offer
    """
    if not is_logged_in() or session['type'] != 'driver':
        return redirect(url_for('login'))

    if request.method == 'POST':
        origin = request.form['from']
        destination = request.form['to']
        date = request.form['date']
        time = request.form['time']
        seats = request.form['seats']
        driver_id = session['email'] # driver id

        # save ride to database
        response = api_create_ride(origin, destination, driver_id, date, time, seats)
        response_body = json.loads(response['body'])

        if response == 'Error: Something went wrong':
            flash('Something went wrong')
            return redirect(url_for('create_rides'))
        else:
            flash('Ride created successfully')
        
        if check_driver_rides(driver_id):
            driver_rides = get_driver_rides(driver_id)
            if driver_rides is not None:
                driver_rides.append(response_body['Item'])
            else:
                driver_rides = [response_body['Item']]
            save_driver_rides(driver_id, driver_rides)
        else:
            save_driver_rides(driver_id, response_body['Item'])

        return redirect(url_for('create_rides'))
    
    return render_template('create_rides.html')

@application.route('/rides/history', methods=['GET', 'POST'])
def ride_history():
    """
    Manage ride offers
    """
    if not is_logged_in() or session['type'] != 'driver':
        return redirect(url_for('login'))

    # get all rides from the driver
    driver_id = session['email']
    
    if check_driver_rides(driver_id):
        rides = get_driver_rides(driver_id)
    else:
        rides = api_get_all_driver_rides(driver_id)
        save_driver_rides(driver_id, rides)

    if rides is not None:
        # sort by most recent date
        rides = sorted(rides, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), reverse=True)
    
    return render_template('ride_history.html', rides=rides)

@application.route('/rides', methods=['GET', 'POST'])
def all_rides():
    """
    See all available rides
    """
    if not is_logged_in():
        return redirect(url_for('login'))

    if check_rides():
        rides = get_all_rides()
    else:
        rides = api_get_all_rides()
        save_rides(rides)

    # filter rides to include only those after today
    today = datetime.today().date()
    filtered_rides = [ride for ride in rides if datetime.strptime(ride['date'], '%Y-%m-%d').date() > today]

    return render_template('all_rides.html', rides=filtered_rides)

@application.route('/rides/join', methods=['GET', 'POST'])
def join_ride():
    """
    Join a ride
    """
    if request.method == 'POST':
        ride_id = request.form['ride_id']
        passenger_id = session['email']
        driver_id = None

        response = api_join_ride(ride_id, passenger_id)
        if response == 'Error: Something went wrong':
            flash('Something went wrong')
            return redirect(url_for('all_rides'))
        else:
            flash('Ride joined successfully')
            # update rides in session
            rides = get_all_rides()

            # find ride in rides
            for ride in rides:
                if ride['ride_id'] == ride_id:
                    ride['passengers'].append(passenger_id)
                    ride['seats'] -= 1
                    # get driver id
                    driver_id = ride['driver_id']

            save_rides(rides)

            if check_driver_rides(driver_id):
                driver_rides = get_driver_rides(driver_id)
                # find ride in driver rides
                for ride in driver_rides:
                    if ride['ride_id'] == ride_id:
                        ride['passengers'].append(passenger_id)
                        ride['seats'] -= 1

            return redirect(url_for('all_rides'))
    

### API functions ###

# call user API that triggers login lambda function
def api_login(email: str, password: str) -> dict:
    query_string = f'email={email}&password={password}'
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/prod/login?' + query_string
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return (response.json())[0]
    else:
        if response.status_code == 404:
            return None
        return 'Error: Something went wrong'
    
# call user API that triggers register lambda function
def api_register(email: str, name: str, phone: int, password: str, user_type: str, car: str = None, license_plate: str = None) -> dict:
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/prod/register?'
    body = {
        'email': email,
        'name': name,
        'phone': phone,
        'password': password,
        'type': user_type
    }
    if car and license_plate:
        body['car'] = car
        body['license_plate'] = license_plate

    response = requests.post(api_url, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        if response.status_code == 404:
            return response.json()['message']
        return 'Error: Something went wrong'
    
def api_get_all_rides() -> dict:
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/prod/rides'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return 'Error: Something went wrong'
    
def api_get_all_driver_rides(email: str) -> dict:
    query_string = f'driver_id={email}'
    api_url = f'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/prod/rides?' + query_string
    response = requests.get(api_url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return 'Error: Something went wrong'
    
def api_create_ride(origin: str , dest: str, email: str, date, time, seats) -> dict:
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/prod/rides'
    passengers = []
    body = {
        'origin': origin,
        'destination': dest,
        'driver_id': email,
        'date': date,
        'time': time,
        'seats': int(seats),
        'passengers': passengers
    }

    response = requests.post(api_url, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
        if response.status_code == 404:
            return response.json()['message']
        return 'Error: Something went wrong'
    
def api_join_ride(ride_id: str, passenger_id: str) -> dict:
    api_url = 'https://hrsnw6fon5.execute-api.us-east-1.amazonaws.com/prod/bookings'
    body = {
        'ride_id': ride_id,
        'passenger_id': passenger_id
    }

    response = requests.post(api_url, json=body)
    
    if response.status_code == 200:
        return response.json()
    else:
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

def check_rides() -> bool:
    if 'rides' in session:
        return True
    return False

def get_all_rides() -> dict:
    return session.get('rides')

def save_rides(rides: dict) -> None:
    session['rides'] = rides

# save driver rides to session
def check_driver_rides(email: str) -> bool:
    if email in session:
        return True
    return False

def get_driver_rides(email: str) -> dict:
    return session.get(email)

def save_driver_rides(email: str, rides: dict) -> None:
    session[email] = rides

if __name__ == '__main__':
    application.run(debug=True)