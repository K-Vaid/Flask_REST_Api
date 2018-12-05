from flask import Flask, jsonify, request,session
from flask_bcrypt import check_password_hash
# from cryptography.fernet import Fernet
from Crypto.Cipher import AES
from bson import json_util
import base64
import models
import json

def user_login():
    try:
        if 'login Status' in session:
            return jsonify({"response": "Already Logged In"})
        else:
            if 'apiKey' in request.json:
                api_key = request.json.get('apiKey')
                if 'secretkey' in request.json and 'email' in request.json and 'password' in request.json:
                    secret_key = request.json.get('secretkey')
                    if api_key is None or secret_key == "":
                        return jsonify({"response": "Invalid Credentials"})
                    else:
                        try:
                            key_verf = models.api_vald(api_key=api_key, secret_key=secret_key)
                            if key_verf == "Api key Verified":
                                user_api = models.mydb.Os_ver.find_one({"api_key" : api_key})
                                client = user_api['client']
                                email = request.json.get('email')
                                password = request.json.get('password')
                                if email == "" or password == "":
                                    return jsonify({"response": "Please fill all the feilds carefully"})
                                else:
                                    # dec_pas = password.decode('hex')
                                    try:
                                        verify = models.mydb.User.find_one({"Client Name" : client, "email" : email}, {"_id":0})
                                        if verify:
                                            _verify = models.mydb.User.find_one({"Client Name" : client, "email" : email})
                                            password_db = _verify['password']
                                            otp_status = _verify['OTP_Verf']
                                            login_status = _verify['logged_in']
                                            if login_status == 'False':
                                                key = "\xd4\xe6\x1a\x83\x1d\xf7\xa43\xf0\xe3)j\x06\xa7/\xba"
                                                IV = "Q\xb9\x11mk\x08*\xd1\n4N\x13\x05n\xc4^"
                                                cipher_suit = AES.new(key, AES.MODE_CFB, IV)
                                                # pas = password.encode('utf-8')
                                                pas = base64.b64decode(password)
                                                dec_pas = cipher_suit.decrypt(pas)
                                                password_verf = check_password_hash(password_db, dec_pas)
                                                if otp_status == 'Verified':
                                                    if password_verf == True:
                                                        logged_in = 'True'
                                                        session['User'] = email
                                                        session['Client'] = client
                                                        session['login Status'] = logged_in
                                                        lst_sid = _verify['Current SID']
                                                        session_db = models.mydb.User.update({"Client Name" : session['Client'], "email" : session['User']}, {"$set": {"logged_in" : session['login Status'], "Last SID" : lst_sid, "Current SID" : session.sid}})
                                                        return jsonify({"Session Id" : session.sid, "response": "Login Successful"})
                                                    else:
                                                        logged_in ='False'
                                                        return jsonify({"response": "Your email or password doesn't match"})
                                                else:
                                                    logged_in ='False'
                                                    return jsonify({"response": "Your OTP is not Verified"})
                                            else:
                                                session['User'] = email
                                                session['Client'] = client
                                                session['login Status'] = 'True'
                                                # models.mydb.sessions.update({"sid" : session.sid}, {"$set": {"Last Used" : datetime.now()}})
                                                # this is to be added for the apis to be used after login.
                                                return jsonify({"response": "User Already Logged In"})
                                        else:
                                            logged_in ='False'
                                            return jsonify({"response": "Your email or password doesn't match"})
                                    except Exception as e:
                                        return "Error Occured: {}".format (str(e))
                            else:
                                return jsonify({"response": key_Verf})
                        except Exception as e:
                            return "Error Occured: {}".format (str(e))
                else:
                    return jsonify({"response": "Incomplete JSON data"})
            else:
                raise ValueError ('Invalid Argument List')
    except Exception as e:
        return "Error Occured: {}".format (str(e))
