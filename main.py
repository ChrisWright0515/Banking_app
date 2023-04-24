import hashlib
import re
import json

import flask
from flask import Flask, render_template, request, session, url_for, redirect, make_response
from sqlalchemy import Column, INTEGER, String, Numeric, Float, create_engine, text
from functions import *

# pip install flask
# pip install flask-sqlalchemy
# pip install mysqlclient

app = Flask(__name__)
# CODE
db_url = 'mysql://root:0515@localhost/Bank_App'
engine = create_engine(db_url, echo=True)
conn = engine.connect()
app.secret_key = generate_random_string(10)


@app.route('/')
def show_home():
    resp = make_response(render_template('base.html'))
    if "account" in session:
        session.pop("account")
    if "details" in session:
        session.pop("details")
    if "info" in session:
        session.pop("info")
    resp.set_cookie('message', expires=0, max_age=0)
    return resp


@app.route('/register', methods=['GET'])
def show_login_form():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def create_user():
    username = request.form.get('username')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    social = request.form.get('ssn')
    address = request.form.get('address')
    phone = request.form.get('phone_number')
    password = request.form.get('password')
    hash_pass = hashing(password).hexdigest()
    if username != '' and first_name != '' and last_name != '' and social != '' and address != '' and phone != '' and password != '':
        if username.lower() != 'admin':
            dupe_username = conn.execute(
                text(f'Select username from users where username = \'{username.lower()}\'')).all()
            hash_social = hashing(social).hexdigest()
            dupe_social = conn.execute(text(f'Select ssn from users where ssn = \'{hash_social}\'')).all()
            dupe_phone = conn.execute(text(f'Select phone_number from users where phone_number = {phone}')).all()
            if len(dupe_username) < 1:
                if len(dupe_social) < 1:
                    if len(dupe_phone) < 1:
                        if len(phone) >= 10:
                            if check_pass(password) == 'Good':
                                conn.execute(text(
                                    f'Insert into users (username,first_name,last_name,ssn,address,phone_number,password) values (\'{username.lower()}\',\'{first_name.title()}\',\'{last_name.title()}\',\'{hash_social}\',\'{address}\',{phone},\'{hash_pass}\')'))
                                conn.commit()
                                message = 'Account added. Please wait to be approved to log in.'
                                return render_template('register.html', message=message)
                            elif check_pass(password) == 'Num':
                                message = 'Password must contain at least 1 Number.'
                                return render_template('register.html', message=message)
                            elif check_pass(password) == 'Lower':
                                message = 'Password must contain at least 1 Lowercase Letter.'
                                return render_template('register.html', message=message)
                            elif check_pass(password) == 'Upper':
                                message = 'Password must contain at least 1 Uppercase Letter.'
                                return render_template('register.html', message=message)
                            elif check_pass(password) == 'Special':
                                message = 'Password must contain at least 1 Special Character.'
                                return render_template('register.html', message=message)
                            else:
                                message = 'Password must be at least 8 characters long.'
                                return render_template('register.html', message=message)
                        else:
                            message = 'Please enter 10 digit phone number.'
                            return render_template('register.html', message=message)
                    else:
                        message = 'That Phone Number is already linked to an account.'
                        return render_template('register.html', message=message)
                else:
                    message = 'That SSN is already linked to an account.'
                    return render_template('register.html', message=message)
            else:
                message = 'That username already exists.'
                return render_template('register.html', message=message)
        else:
            message = 'That username already exists.'
            return render_template('register.html', message=message)
    else:
        message = 'Please fill out all fields.'
        return render_template('register.html', message=message)


@app.route('/login', methods=['GET'])
def show_login():
    resp = make_response(render_template('login.html'))
    if "account" in session:
        session.pop("account")
    if "details" in session:
        session.pop("details")
    print(session)
    if "info" in session:
        session.pop("info")
    resp.set_cookie('message', expires=0, max_age=0)
    return resp


@app.route('/login', methods=['POST'])
def login():
    if "account" in session:
        session.pop("account")
    if "details" in session:
        session.pop("details")
    if "info" in session:
        session.pop("info")
    username = request.form.get('username')
    password = request.form.get('password')
    usernames = conn.execute(text('select username from users')).all()
    if username == 'Admin' and password == 'AdminPass':
        resp = make_response(redirect(url_for('show_admin_page')))
        accounts = conn.execute(text('Select * from users')).all()
        details = conn.execute(text(f'Select * from accounts')).all()
        all_accounts = format_account_cookies(accounts)
        all_details = format_details_cookies(details)
        session["account"] = all_accounts
        session["details"] = all_details
        return resp
    else:
        for name in usernames:
            if username.lower() == name[0].lower():
                user_password = conn.execute(text(f'Select password from users where username = \'{username}\'')).all()
                hash_pass = hashing(password).hexdigest()
                if hash_pass == user_password[0][0]:
                    status = conn.execute(text(f'select status from users where username = \'{username}\'')).all()
                    if status[0][0] == 'APR':
                        resp = make_response(redirect(url_for('show_user_page')))
                        session["info"] = name[0]
                        return resp
                    else:
                        message = 'You must be approved before you can login'
                        return render_template('login.html', message=message)
                else:
                    message = 'Incorrect Password'
                    return render_template('login.html', message=message)
        else:
            message = 'Username does not exist'
            return render_template('login.html', message=message)


@app.route('/account/')
def show_user_page():
    message = request.cookies.get('message')
    if "info" in session:
        info = session["info"]
        current_balance = conn.execute(
            text(f'Select balance from accounts natural join users where username = \'{info}\'')).all()
        balance = f'{current_balance[0][0]:,.2f}'
        account_info = conn.execute(
            text(f'select * from users natural join accounts where username = \'{info}\'')).all()
        number = str(account_info[0][6])
        phone_number = phone_format(number)
        return render_template('user_page.html', details=account_info[0], phone_number=phone_number, balance=balance,
                               message=message)
    else:
        resp = make_response(redirect(url_for('show_login')))
        return resp


@app.route('/admin')
def show_admin_page():
    if 'account' in session:
        accounts = session['account']
        details = session['details']
        resp = make_response(
            render_template('admin_page.html', phone_format=phone_format, accounts=accounts, details=details))
        return resp
    else:
        resp = make_response(redirect(url_for('show_login')))
        return resp


@app.route('/admin/confirm_<user_no>', methods=['GET'])
def approve_user(user_no):
    if 'account' in session:
        conn.execute(text(f'Update users set status = \'APR\' where user_no = {user_no}'))
        conn.commit()
        locked_user = conn.execute(text(f'Select account_no from accounts where user_no = {user_no}')).all()
        if len(locked_user) < 1:
            conn.execute(text(f'Insert into accounts (user_no) values ({user_no})'))
            conn.commit()
        accounts = conn.execute(text('Select * from users')).all()
        details = conn.execute(text(f'Select * from accounts')).all()
        resp = make_response(redirect(url_for('show_admin_page')))
        all_accounts = format_account_cookies(accounts)
        all_details = format_details_cookies(details)
        session["account"] = all_accounts
        session["details"] = all_details
        return resp
    else:
        resp = make_response(redirect(url_for('show_login')))
        return resp


@app.route('/account/deposit', methods=['GET'])
def show_deposit_form():
    if 'info' in session:
        username = session["info"]
        return render_template('deposit.html', username=username)
    else:
        resp = make_response(redirect(url_for('show_login')))
        return resp


@app.route('/account/deposit', methods=['POST'])
def deposit_money():
    if 'info' in session:
        username = session["info"]
        card_no = request.form.get('card_no')
        exp_date = request.form.get('exp_date')
        ccv = request.form.get('ccv')
        amt = request.form.get('amt')
        if card_no != '':
            if exp_date != '':
                if ccv != '':
                    if amt != '':
                        conn.execute(text(
                            f'update accounts set balance = (balance + {amt}) where user_no in (select user_no from users where username = \'{username}\')'))
                        conn.commit()
                        message = 'Deposit Successful'
                        return render_template('deposit.html', username=username, message=message)
                    else:
                        message = 'Please Enter Deposit Amount'
                        return render_template('deposit.html', username=username, message=message)
                else:
                    message = 'Please enter CCV'
                    return render_template('deposit.html', username=username, message=message)
            else:
                message = 'Please enter expiration date'
                return render_template('deposit.html', username=username, message=message)
        else:
            message = 'Please enter card number'
            return render_template('deposit.html', username=username, message=message)
    else:
        resp = make_response(redirect(url_for('show_login')))
        return resp


@app.route('/account/send', methods=['GET'])
def show_send_form():
    if 'info' in session:
        username = session["info"]
        return render_template('send_money.html', username=username)
    else:
        resp = make_response(redirect(url_for('show_login')))
        return resp


@app.route('/account/send', methods=['POST'])
def send_money():
    username = session["info"]
    search = request.form.get('search_user')
    amt = request.form.get('amt_send')
    if amt != '':
        if search.isdigit():
            check_phone = conn.execute(text(f'Select phone_number from users where phone_number = {search}')).all()
            if len(check_phone) > 0:
                check_funds = conn.execute(text(
                    f'select balance from accounts where user_no in (select user_no from users where username = \'{username}\')')).all()
                if float(check_funds[0][0]) >= float(amt):
                    phone = str(check_phone[0][0])
                    resp = make_response(redirect(url_for('confirm_send')))
                    resp.set_cookie('amt', amt)
                    resp.set_cookie('phone', phone)
                    resp.set_cookie('counter', '10')
                    return resp
                else:
                    message = 'Insufficient Funds'
                    return render_template('send_money.html', username=username, message=message)
            else:
                message = 'No accounts match that Phone number'
                return render_template('send_money.html', username=username, message=message)

        elif search.isalnum():
            check_username = conn.execute(text(f'Select username from users where username = \'{search}\'')).all()
            if len(check_username) > 0:
                check_funds = conn.execute(text(
                    f'select balance from accounts where user_no in (select user_no from users where username = \'{username}\')')).all()
                if float(check_funds[0][0]) > float(amt):
                    search_user = check_username[0][0]
                    resp = make_response(redirect(url_for('confirm_send')))
                    resp.set_cookie('amt', amt)
                    resp.set_cookie('username', search_user)
                    resp.set_cookie('counter', '10')
                    return resp
                else:
                    message = 'Insufficient Funds'
                    return render_template('send_money.html', username=username, message=message)
            else:
                message = 'No accounts match that Username'
                return render_template('send_money.html', username=username, message=message)
        else:
            message = 'Please fill out all fields'
            return render_template('send_money.html', username=username, message=message)
    else:
        message = 'Please fill out all fields'
        return render_template('send_money.html', username=username, message=message)


@app.route('/account/confirm', methods=['GET'])
def show_confirm_form():
    if 'amt' in request.cookies:
        amt = request.cookies.get('amt')
        username = session["info"]
        if 'phone' in request.cookies:
            phone = request.cookies.get('phone')
            phone_number = int(phone)
            recipient = conn.execute(
                text(
                    f'select concat(first_name, \' \', last_name) from users where phone_number = {phone_number}')).all()
            return render_template('confirm_send.html', amt=f'{float(amt):,.2f}', phone=phone,
                                   recipient=recipient[0][0])
        else:
            user = request.cookies.get('username')
            recipient = conn.execute(
                text(f'select concat(first_name, \' \', last_name) from users where username = \'{user}\'')).all()
            return render_template('confirm_send.html', amt=f'{float(amt):,.2f}', user=user, recipient=recipient[0][0])
    else:
        return redirect(url_for('show_user_page'))


@app.route('/account/confirm', methods=['POST'])
def confirm_send():
    count = request.cookies.get('counter')
    counter = int(count)
    amt = request.cookies.get('amt')
    username = session["info"]
    verify_ssn = conn.execute(text(f'select ssn from users where username = \'{username}\'')).all()
    ssn = request.form.get('confirm_ssn')
    if 'phone' in request.cookies:
        phone = request.cookies.get('phone')
        recipient = conn.execute(
            text(f'select concat(first_name, \' \', last_name) from users where phone_number = {phone}')).all()
        hash_ssn = hashing(ssn).hexdigest()
        if hash_ssn == verify_ssn[0][0]:
            conn.execute(text(
                f'Update accounts set balance = (balance - {amt}) where user_no in (select user_no from users where username = \'{username}\')'))
            conn.execute(
                text(
                    f'Update accounts set balance = (balance + {amt}) where user_no in (select user_no from users where phone_number = {phone})'))
            conn.commit()
            amt_format = f'{float(amt):,.2f}'
            message = f'Successfully sent ${amt_format} to {recipient[0][0]}.'
            resp = make_response(redirect(url_for('show_user_page')))
            resp.set_cookie('message', message, max_age=60)
            resp.set_cookie('phone', expires=0)
            resp.set_cookie('amt', expires=0)
            resp.set_cookie('counter', expires=0)
            return resp
        else:
            if counter < 1:
                message = f'Transfer unsuccessful.'
                resp = make_response(redirect(url_for('show_user_page')))
                resp.set_cookie('message', message, max_age=60)
                resp.set_cookie('phone', expires=0)
                resp.set_cookie('amt', expires=0)
                resp.set_cookie('counter', expires=0)
                return resp
            else:
                counter -= 1
                message = f'Incorrect {counter} chances left.'
                resp = make_response(render_template('confirm_send.html', message=message, amt=amt, phone=phone,
                                                     recipient=recipient[0][0]))
                resp.set_cookie('counter', str(counter))
                return resp
    else:
        user = request.cookies.get('username')
        recipient = conn.execute(
            text(f'select concat(first_name, \' \', last_name) from users where username = \'{user}\'')).all()
        hash_ssn = hashing(ssn).hexdigest()
        if hash_ssn == verify_ssn[0][0]:
            conn.execute(text(
                f'Update accounts set balance = (balance - {amt}) where user_no in (select user_no from users where username = \'{username}\')'))
            conn.execute(
                text(
                    f'Update accounts set balance = (balance + {amt}) where user_no in (select user_no from users where username = \'{user}\')'))
            conn.commit()
            amt_format = f'{float(amt):,.2f}'
            message = f'Successfully sent ${amt_format} to {recipient[0][0]}.'
            resp = make_response(redirect(url_for('show_user_page')))
            resp.set_cookie('message', message, max_age=60)
            resp.set_cookie('username', expires=0)
            resp.set_cookie('amt', expires=0)
            resp.set_cookie('counter', expires=0)
            return resp
        else:
            if counter < 1:
                message = f'Transfer unsuccessful.'
                resp = make_response(redirect(url_for('show_user_page')))
                resp.set_cookie('message', message, max_age=60)
                resp.set_cookie('username', expires=0)
                resp.set_cookie('amt', expires=0)
                resp.set_cookie('counter', expires=0)
                return resp
            else:
                counter -= 1
                message = f'Incorrect {counter} chances left.'
                resp = make_response(render_template('confirm_send.html', message=message, amt=amt, user=user,
                                                     recipient=recipient[0][0]))
                resp.set_cookie('counter', str(counter))
                return resp


@app.route('/logout')
def log_out():
    resp = make_response(redirect(url_for('show_home')))
    if "info" in session:
        session.pop("info")
    resp.set_cookie('message', expires=0, max_age=0)
    if "account" in session:
        session.pop("account")
    if "details" in session:
        session.pop("details")
    return resp


if __name__ == '__main__':
    app.run(debug=True)
