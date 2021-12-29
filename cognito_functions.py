from boto3 import client
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv, find_dotenv
#load the environmental variables to keep us nice and secure! 
load_dotenv(find_dotenv())
from pycognito import Cognito
from datetime import datetime

access_key=os.getenv("access_key")
secret_key=os.getenv("secret_key")

user_pool_id = 'Cognito_pool_id_replace_me'
client_id = 'Cognito_client_id_replace_me'

def register_new_user(email_entered, password_entered):
    """uses pycognito to register a new user in the database"""
    try:
        u = Cognito(user_pool_id, client_id, access_key=access_key, secret_key=secret_key, username=email_entered)
        username_entered = email_entered.split("@")[0]
        u.set_base_attributes(email=email_entered, preferred_username=username_entered)
        u.register(email_entered, password_entered )
        return True, None
    except Exception as e:
        print(e)
        return False, e

def log_user_out(current_user_object):
    """logs a user out of the system"""
    try:
        u = Cognito(user_pool_id, client_id, id_token=current_user_object.id_token, refresh_token=current_user_object.refresh_token,    access_token=current_user_object.access_token)
        u.logout()
        return True

    except Exception as e:
        print(e)
        return False


def authenticate_user(email_entered, password_entered):
    """uses pycognito to authenticate a user"""
    try:
        u = Cognito(user_pool_id, client_id, username=email_entered)

        u.authenticate(password=password_entered)
        return u, True
    except Exception as e:
        print(e)
        return None, False


def start_reset_password(email_entered):
    """helps the user reset their password"""
    try:
        u = Cognito(user_pool_id, client_id, username=email_entered)
        u.initiate_forgot_password()
        return True, None

    except Exception as e:
        print(e)
        return False, e


def confirm_reset_password(email_entered, one_time_passcode, new_password):
    """helps the user reset their password"""
    try:
        u = Cognito(user_pool_id, client_id, username=email_entered)
        u.confirm_forgot_password(one_time_passcode, new_password)
        return True, None

    except Exception as e:
        print(e)
        return False, e


def get_list_of_user_emails():
    """returns a list of all the emails in our pool"""
    u = Cognito(user_pool_id, client_id, access_key=access_key, secret_key=secret_key)
    return [user.email for user in u.get_users(attr_map={"email":"email"})]


def send_an_email(email_address, BODY_TEXT):
    """sends an email using the contact form"""
    # This address must be verified with Amazon SES.
    SENDER = "your_email_here@gmail.com"
    RECIPIENT = "your_email_here@gmail.com"
    SUBJECT = "Contact Form"
    BODY_HTML = """<html>    <head>This email was generated from  {}.</head>    <body>    <p>{}</p>    </body>    </html> """.format(email_address, BODY_TEXT)            

    try:
        #Provide the contents of the email.
        response = client('ses', region_name="us-east-1", aws_access_key_id=os.getenv("access_key"),    aws_secret_access_key=os.getenv("secret_key")).send_email(
            Destination={  'ToAddresses': [ RECIPIENT  ] },
            Message={'Body': {
                        'Html': { 'Charset': "UTF-8", 'Data': BODY_HTML },
                        'Text': { 'Charset': "UTF-8", 'Data': BODY_TEXT  }, },
                        'Subject': { 'Charset': "UTF-8", 'Data': SUBJECT}, }, Source=SENDER )

    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
        return False
    else:
        print("Email sent! Message ID:")
        return True

def password_check(password): 
    """based on AWS Cognito specifications :    Minimum length 8
    Require numbers --- True   |   Require special character--- True
    Require uppercase letters--- True | Require lowercase letters--- True"""
    #check length greater than 8
    if len(password) < 8: 
        return False, 'length should be at least 8'
    #check length less than 45 because we don't want some sql injection or something      
    if len(password) > 45: 
        return False, 'length should be not be greater than 45 characters'
    #check if there is a digit      
    if not any(char.isdigit() for char in password): 
        return False, 'Password should have at least one numeral'
    #check if there is an upper character     
    if not any(char.isupper() for char in password): 
        return False, 'Password should have at least one uppercase letter'
    #check if there is a lower character
    if not any(char.islower() for char in password): 
        return False, 'Password should have at least one lowercase letter'
    #check if there is a special symbol
    if not any(char in ['$', '@', '#', '%', "|", "+", "=","-","_", "*", "&", "!", "^", "(", ")", "?"]  for char in password): 
        return False, 'Password should have at least one of the symbols "$ @ # % | + = - _ * & ! ^ ( ) ?'
   
    return True, None
