import hashlib
import random
import string
import json
from cryptography.fernet import Fernet



def phone_format(n):
    if (len(n)) == 10:
        new_phone = f'({n[0:3]}) {n[3:6]}-{n[6:]}'
        return new_phone
    else:
        return n


def check_pass(password):
    char = '[@_!#$%^&*()<>?/\|}{~:]'
    spec_char = list(char)
    special = False
    upper = False
    lower = False
    num = False
    for letter in password:
        if letter.isupper():
            upper = True
        elif letter in spec_char:
            special = True
        elif letter.islower():
            lower = True
        elif letter.isdigit():
            num = True
    if len(password) >= 8:
        if special:
            if upper:
                if lower:
                    if num:
                        return 'Good'
                    else:
                        return 'Num'
                else:
                    return 'Lower'
            else:
                return 'Upper'
        else:
            return 'Special'
    else:
        return 'Length'


def hashing(password):
    return hashlib.sha3_256(password.encode())


def generate_random_string(length):
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for i in range(length))
    return random_string


def format_account_cookies(row):
    all_accounts = []
    for account in row:
        each_acc = []
        for i in range(len(account)):
            each_acc.append(account[i])
        all_accounts.append(each_acc)
    return all_accounts


def format_details_cookies(row):
    all_details = []
    for detail in row:
        each_detail = []
        for i in range(len(detail)):
            if i == 2:
                each_detail.append(float(detail[i]))
            else:
                each_detail.append(detail[i])
        all_details.append(each_detail)
    return all_details



