from flask_bcrypt import generate_password_hash, check_password_hash
from flask import Flask, jsonify, session
from pymongo import MongoClient
import datetime
import json
import os

client = MongoClient('localhost', 27017)
mydb = client.IOT_database_New

Os_ver = mydb.IOT_database_New
User = mydb.IOT_database_New
Activation = mydb.IOT_database_New
Data = mydb.IOT_database_New

# bcrypt = Bcrypt(None)
#sid_log = open("Sid_Log.txt", 'a')

def create_user(email, phone, client):
    try:
        if email == "" or phone == "":
            return "Please fill all the feilds carefully"
        else:
            unique_email = mydb.User.find_one({"Client Name" : client, "email" : email}, {"_id":0})
            unique_phone = mydb.User.find_one({"Client Name" : client, "phone" : phone}, {"_id":0})
            if unique_email or unique_phone:
                return "Email or Phone already exists."
                # raise ValueError ("Email or Phone already exists.")
            else:
                mydb.User.insert(
                    {
                    "email" : email,
                    "phone" : phone,
                    "Client Name" : client,
                    "password" : "Not set",
                    "Account" : "Inactive",
                    "OTP_Verf" : "Not Verified",
                    "Current SID": session.sid,
                    "Last SID": session.sid,
                    "logged_in" : "False",
                    "Date-Time" : datetime.datetime.now()
                    })
                session['Reg_Phase'] = "Not Verified"
                #sid_log.write("["+str(datetime.now())+"]"+ str(session.sid)+ " User Creation"+"\n")
                # session['Account'] = "Inactive"
                return session.sid
                # return jsonify({"Session_id": sid})
    except Exception as e:
        return "Error Occured: {}".format (str(e))

def add_password(sid, password):
    try:
        user_sid = mydb.User.find_one({"Current SID" : sid}, {"_id":0})
        user = user_sid['email']
        password_hash = generate_password_hash(password)
        if user_sid:
            mydb.User.update({"email" : user}, {"$set": {"password" : password_hash}})
            # session.clear()
            # mydb.User.update({"email" : user}, {"$unset": {"SID" : sid}})
            return jsonify({"response": "Registered Successfully"})
        else:
            return jsonify({"response": "Invalid session id"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))

def user_link(email, client, otp, activation_link=None):
    try:
        exists = mydb.Activation.find_one({"Client Name" : client, "email" : email}, {"_id":0})
        if exists:
            if activation_link == None:
                mydb.Activation.update({"Client Name" : client, "email" : email}, {"$set": {"Date-Time": datetime.datetime.now(), "OTP" : otp}})
                return jsonify({"response": "Updated Successfully"})
            else:
                mydb.Activation.update({"Client Name" : client, "email" : email}, {"$set": {"Date-Time": datetime.datetime.now(), "activation_link" : activation_link, "OTP" : otp}})
                return jsonify({"response": "Updated Successfully"})
        else:
            mydb.Activation.insert(
                {
                "Client Name" : client,
                "email" : email,
                "activation_link" : activation_link,
                "OTP" : otp,
                "Date-Time" : datetime.datetime.now()
                })
            return jsonify({"response": "Added Successfully"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))

def add_data(phone_no, data):
    try:
        mydb.Data.insert(
            {
            "phone_no" : phone_no,
            "data" : data,
            "Submitted_at" : datetime.datetime.now(),
            })
        # exists = mydb.Data.find_one({"phone_no" : phone_no}, {"_id":0})
        # if exists:
        #     mydb.Data.update({"phone_no" : phone_no}, {"$set": {"Received_at": datetime.datetime.now()}})
        #     return jsonify({"response": "Date added"})
        # else:
        #     return jsonify({"response": "Date not added"})
        return jsonify({"response": "Data added Successfully"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))

def apikey_auth(client):
    try:
        client_name = mydb.Os_ver.find_one({"client" : client}, {"_id":0})
        # os_name2 = mydb.Os_ver.find_one({"OS Name" : "IOS"}, {"_id":0})
        if client_name:
            return "Client Already Exists"
        else:
            Apikey = os.urandom(24).encode('hex')
            Secretkey = generate_password_hash(Apikey)
            mydb.Os_ver.insert(
                {
                "api_key" : Apikey,
                "secret_key" : Secretkey,
                "client" : client
                })
            return jsonify({"Api Key": Apikey, "Secret key" : Secretkey})
    except Exception as e:
        return "Error Occured: {}".format (str(e))

def api_vald(api_key, secret_key):
    try:
        api_auth = mydb.Os_ver.find_one({"api_key" : api_key}, {"_id":0})
        if api_auth:
            key_db = mydb.Os_ver.find_one({"api_key" : api_key})
            secret_db = key_db['api_key']
            key_verf = check_password_hash(secret_key, secret_db)
            if key_verf:
                return "Api key Verified"
            else:
                return "Key Mismatch"
        else:
            return "Key not Found"
    except Exception as e:
        return "Error Occured: {}".format (str(e))
#sid_log.close()

def recreate_session(sid):
    try:
        s_id = mydb.sessions.find_one({"sid" : sid}, {"_id":0})
        session_var = s_id.get('data')
        session['client'] = session_var['client']
        session['user'] = session_var['user']
        session['Reg_Phase'] = session_var['Reg_Phase']
        session['sent_at'] = session_var['sent_at']
        if 'Account' in session_var:
            session['Account'] = session_var['Account']
        mydb.User.update({"Client Name" : session['client'], "email" : session['user']}, {"$set": {"Last SID" : sid, "Current SID" : session.sid}})
        return jsonify({"error-message": "Session Expired. New session created.", "Session ID" : session.sid})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
