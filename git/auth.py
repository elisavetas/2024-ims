import getpass
import hashlib
import json
import pathlib
import random
import string
import sys
import tempfile

# name of the file where we store the pw database
PWDB_FLNAME = pathlib.Path('pwdb.json')

# the pw database will be stored in the local directory
PWDB_DEFAULTPATH =  PWDB_FLNAME

def err(text, status):
    sys.stderr.write(f'{sys.argv[0]}: {text}!\n')
    sys.exit(status)

def get_credentials():
    # get input from terminal
    username = input('Enter your username: ')
    # get password using the appropriate module, so that typed characters are not
    # echoed to the terminal
    password = getpass.getpass('Enter your password: ')
    return (username, password)

def authenticate(username, pass_text, pwdb):
    success = False
    if username in pwdb:
        salt = pwdb[username]["salt"]
        # calculate hash and compare with stored hash
        if pwhash(pass_text, salt) == pwdb[username]["hash"]:
            success = True
    return success

def add_user(username, password, pwdb, pwdb_path):
    # do not try to add a username twice
    if username in pwdb:
        err(f'Username already exists [{username}]', 2)
    else:
        uniq_salt = get_salt()
        pwdb[username] = {"hash": pwhash(password, uniq_salt),
                          "salt": uniq_salt}
        write_pwdb(pwdb, pwdb_path)


def read_pwdb(pwdb_path):
    # try to read from the database
    # if anything happens, report the error!
    try:
        with open(pwdb_path, 'rt') as pwdb_file:
            pwdb = json.load(pwdb_file)
    except json.decoder.JSONDecodeError as exc:
        # this happens when the json data is invalid
        err(f'Invalid database {pwdb_path}: {exc}', 3)
    except Exception as exc:
        # this is a catch-all condition
        err(f'Error reading {pwdb_path}: {exc}', 4)
    return pwdb

def write_pwdb(pwdb, pwdb_path):
    with open(pwdb_path, 'wt') as pwdb_file:
        json.dump(pwdb, pwdb_file)


def pwhash(password, salt):
    # encode to bytes
    pass_text = password + salt
    bpass = pass_text.encode('utf8')
    return hashlib.sha256(bpass).hexdigest() 


def get_salt():
    salt = ""
    for _ in range(5):
        num = random.randrange(65, 123)
        salt += chr(num)
    return salt



if __name__ == '__main__':
    # ask for credentials
    username, password = get_credentials()

    # if the database does not exist yet, create an empty one by default
    if not PWDB_DEFAULTPATH.exists():
        write_pwdb({}, PWDB_DEFAULTPATH)

    # load the password database from file
    pwdb = read_pwdb(PWDB_DEFAULTPATH)

    # try to authenticate
    if authenticate(username, password, pwdb):
        print('Successfully authenticated!')
    elif username not in pwdb:
        # if the user is not known, ask if a new user must be added
        ans = input('Create new user [y/n]? ')
        if ans == 'y':
            add_user(username, password, pwdb, PWDB_DEFAULTPATH)
    else:
        # report wrong password
        err('Wrong password!', 1)