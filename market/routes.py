from datetime import datetime

from flask_wtf.csrf import CSRFError

from market import app
from flask import render_template , redirect , url_for , flash , request , make_response
from typing import Optional
from datetime import datetime, timedelta
import pytz
from jose import jwt, JWTError, ExpiredSignatureError

IST = pytz.timezone('Asia/Kolkata')
SECRET_KEY_JWT = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

from market.forms import RegisterForm, LoginForm , PurchaseItemForm , SellItemForm
from market.models import Item , User
from market import db
from flask_login import login_user , logout_user , login_required , current_user

@app.route('/about/<username>')
def about_page(username):
    return f'<h1>This is the about page of {username}'

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/market',methods=['GET','POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    if request.method == "POST":
        # Purchase Item Logic
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy(current_user)
                flash(f"Congratulations! You purchased {p_item_object.name} for {p_item_object.price}$",
                      category='success')
            else:
                flash(f"Unfortunately, you don't have enough money to purchase {p_item_object.name}!",
                      category='danger')
        # Sell Item Logic
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash(f"Congratulations! You sold {s_item_object.name} back to market!", category='success')
            else:
                flash(f"Something went wrong with selling {s_item_object.name}", category='danger')

        return redirect(url_for('market_page'))

    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items,
                               selling_form=selling_form)

    if request.method == "GET":
        items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')

        token_expires = timedelta(minutes=1)
        token = create_access_token(form.username.data, expires_delta=token_expires)

        token_expires = timedelta(minutes=60)
        refresh_token = create_access_token(form.username.data, expires_delta=token_expires)

        dt = datetime.now(IST) + timedelta(minutes=1)

        response = make_response(redirect('/market'))
        response.set_cookie(key="access_token", value=token)
        response.set_cookie(key="refresh_token", value=refresh_token)
        response.set_cookie(key="access_token_expirationIn", value=str(dt))

        return response
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            print(f'There was an error with creating a user: {err_msg}')
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            token_expires = timedelta(minutes=1)
            token = create_access_token(form.username.data, expires_delta=token_expires)

            token_expires = timedelta(minutes=60)
            refresh_token = create_access_token(form.username.data, expires_delta=token_expires)
            dt = datetime.now(IST) + timedelta(minutes=1)

            response = make_response(redirect('/market'))
            response.set_cookie(key="access_token", value=token)
            response.set_cookie(key="refresh_token", value=refresh_token)
            response.set_cookie(key="access_token_expirationIn", value=str(dt))

            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return response
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))



def create_access_token(username: str,expires_delta: Optional[timedelta] = None):

    encode = {"sub": username}
    if expires_delta:
        expire = datetime.now(IST) + expires_delta
    else:
        expire = datetime.now(IST) + timedelta(minutes=1)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY_JWT, algorithm=ALGORITHM)


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash(f"csrf token not found / mismatch", category='danger')
    return redirect(request.url)#render_template('csrf_error.html', reason=e.description), 400

@app.after_request
def response_check(response):
    return response
