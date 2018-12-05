from flask import Flask, jsonify, request, session
from datetime import timedelta, datetime
import Reg_mid
import smtplib
import random
import models
import json
import os

def Once(email):
    key = os.urandom(24).encode('hex')
    otp = random.randrange(1000, 10000, 3)
    message = """From: Forsk Labs
To:{}
Subject: Forsk IoT Lab
Your OTP is {},use this to verify your Phone Number.
Please click on the below activation link to activate your account.
    http://52.66.142.102:8000/api1.0/activation?activation_key={}.""".format(email,otp,key)
    client = session['client']
    models.user_link(email = email, client=client, activation_link = key, otp = otp)
    return message

def re_send(email):
    otp = random.randrange(1000, 10000, 3)
    message = """From: Forsk Labs
To:{}
Subject: Forsk IoT Lab
Your new OTP is {},use this to verify your Phone Number.""".format(email,otp)
    client = session['client']
    sent_at = datetime.now() + timedelta(minutes=2)
    models.mydb.User.update({"Client Name" : client, "email" : email}, {"$set": {"sent_at" : sent_at}})
    models.user_link(email = email, client=client, otp = otp)
    return message

def mail(email, message):
    sender = 'forsklabs@gmail.com'
    receivers = [email]
    try:
        smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
        smtpObj.starttls()
        smtpObj.login('forsklabs@gmail.com', 'forsk@labs19')
        smtpObj.sendmail(sender, receivers, message)
        sent_at = datetime.now() + timedelta(minutes=2)
        models.mydb.User.update({"Client Name" : session['client'], "email" : session['user']}, {"$set": {"sent_at" : sent_at}})
        session['sent_at'] = sent_at
        print "Mail Sent Successfully"
        return "Mail Sent Successfully"
    except Exception as e:
        excp = str(e)
        _error = "Mail sending Failed: {}.".format(excp)
        print "mailer resp....", _error
        return jsonify({"response2": _error})

def mailer(sid, Resend='True'):
    try:
        if 'client' in session and 'user' in session:
            client = session['client']
            email = session['user']
            otp_stat = session['Reg_Phase']
            if sid == session.sid:
                if 'Account' in session:
                    account_stat = session['Account']
                    if Resend == 'True' and otp_stat != "OTP Verified" and account_stat == "Inactive":
                        session['Reg_Phase'] = "phase 1 complete"
                        message = Once(email=email)
                        return mail(email=email, message=message)
                    else :
                        message = Once(email=email)
                        return mail(email=email, message=message)
                else:
                    if Resend == 'True' and otp_stat != "OTP Verified":
                        session['Reg_Phase'] = "Resent OTP"
                        message = re_send(email = email)
                        return mail(email=email, message=message)
                    elif Resend == 'False':
                        message = Once(email=email)
                        return mail(email=email, message=message)
                    else:
                        return jsonify({"response": "OTP already verified for this User"})
            else:
                return jsonify({"response": "Session Id mismatch"})
        else:
            print "session Expired. Recreating session..."
            new_session = models.recreate_session(sid)
            return new_session
    except Exception as e:
        return "Error Occured: {}".format (str(e))
