import os, sys
import urllib, hashlib

from libgravatar import Gravatar

from flask import Flask, flash, render_template, request, url_for, redirect, jsonify, session
from passlib.hash import sha256_crypt
from sqlalchemy import exc
import pandas as pd

# from flask_heroku import Heroku

app = Flask(__name__)
app.secret_key = "ksg-dwellers"

# Using environment variable, since it can be set manually, and only once
# on local system, but on Heroku, it is already set to the assigned database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", default="postgresql://localhost:5432/dweller")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def landing():
    return render_template('dashboard.html')


@app.route('/index')
def index():
    return render_template('table.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile')
def profile():
    g = Gravatar("gkorodi@gmail.com")
    return render_template('profile.html', gravatar=g.get_image(size=40, default=request.url_root+url_for('static', filename='assets/img/default-avatar.png')))


@app.route('/map')
def map():
    return render_template('map.html')


@app.route('/table')
def table():
    df = pd.read_csv('static/data/fy19fullpropassess.csv')
    props = []
    subset = df.sample(n=137)
    print(subset.columns)
    for row in subset.values.tolist():
        property_details = {
            'address': str(row[3])+' '+row[4]+' '+str(row[5]),
            'bedroom': 1,
            'bathroom': 2,
            'asessment_value': row[19]
            }
        props.append(property_details)
        #props.append({ 'address': row['ST_NAME']})

    return render_template('table.html', properties = props)


# MapBox token: 'pk.eyJ1IjoiZ2tvcm9kaSIsImEiOiJQVnJpQy1RIn0.vReN7nqYyOUn9OSq4cXpjw'
# MapBox style: 'mapbox://styles/gkorodi/ck2xzs29l28tz1cmutax0891r'

# signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    errors = []
    signup_form = SignUpForm()
    if request.method == 'POST':
        errors = []
        if not signup_form.validate():
            errors.append(signup_form.errors)
            print(signup_form.errors)
        else:
            try:
                print('DEBUG adding new user {}'.format(signup_form.username.data))
                new_user = User()
                new_user.username = signup_form.username.data
                print(signup_form.password.data)
                new_user.password = sha256_crypt.hash(signup_form.password.data)
                print(new_user.password)
                print(sha256_crypt.encrypt(signup_form.password.data))

                db.session.add(new_user)
                db.session.commit()
                print('DEBUG saved user {}'.format(signup_form.username.data))

                flash('Thank you <b>{}</b>! You have successfully registered.'.format(
                    signup_form.username.data))
                return redirect(url_for('login'))
            except exc.IntegrityError as ie:
                errors.append("Username already exists.")
            except Exception as e:
                errors.append(
                    'Could not register the username <a href="#" class="alert-link">{}</a>. Sorry! {}'.format(signup_form.username.data, type(e))
                )

    print(signup_form.errors)
    return render_template('signup.html', form=signup_form, errors=errors)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    errors = []
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Handle errors
        if user is None:
            errors.append('Username is not found.')
            return render_template('login.html', title='Login', form=form)

        if not sha256_crypt.verify(password, user.password.strip()):
            errors.append("Invalid password provided.")
            return render_template('login.html', title='Login', form=form)

        session['username'] = username
        return render_template('properties.html')

    else:
        return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('properties'))


# info route
@app.route('/info/<mlsnum>')
def info(mlsnum):
    if 'username' in session:
        session_user = User.query.filter_by(username=session['username']).first()
        listing = Condo.query.filter_by(mlsnum=mlsnum).first()
        # round listing prices
        listing.ppsf = ('n/a' if listing.ppsf is None else '${0:.2f}'.format(listing.ppsf))  # '{0:.2f}'.format(listing.ppsf if type(listing.ppsf) != 'str' or type(listing.ppsf) != 'NoneType' else 0)
        listing.list_price = '${:,.2f}'.format(listing.list_price)
        lp = (listing.predicted_price if isinstance(listing.predicted_price, (int, float)) else 0)
        listing.predicted_price = '{0:,.2f}'.format(lp)
        return render_template('condo.html', listing=listing)
    else:
        # return render_template('index.html', title='Home', posts=posts, session_username=session_user.username)
        return render_template('needlogin.html')


# add the rest of the info route here

def convert_to_dict(obj):
    """
  A function takes in a custom object and returns a dictionary representation of the object.
  This dict representation includes meta data such as the object's module and class names.
  """

    #  Populate the dictionary with object meta data
    obj_dict = {
        "__class__": obj.__class__.__name__,
        "__module__": obj.__module__
    }

    #  Populate the dictionary with object properties
    obj_dict.update(obj.__dict__)
    return obj_dict


@app.route('/listings')
def listings():
    condos = Condo.query.all();
    listings = []
    for condo in condos:
        mcondo = convert_to_dict(condo);
        del mcondo['_sa_instance_state']
        listings.append(mcondo)
        # for k in mcondo.keys():
        # print(k)
        # listings.append()
    return jsonify(listings)


# load_data route (for D3 vis)

if __name__ == "__main__":
    app.run(debug=True)
