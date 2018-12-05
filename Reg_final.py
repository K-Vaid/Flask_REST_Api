from flask import Flask, jsonify, request, session
from datetime import timedelta, datetime
from Crypto.Cipher import AES
import base64
import models
import uuid
import json

def password():
    try:
        # print "is session exist....",session['user']
        if 'apiKey' in request.json and 'sid' in request.json:
            api_key = request.json.get('apiKey')
            Sid = request.json.get('sid')
            if 'Reg_Phase' in session and 'user' in session and 'client' in session:
                if session['Reg_Phase'] == "OTP Verified":
                    if 'secretkey' in request.json and 'password' in request.json:
                        secret_key = request.json.get('secretkey')
                        password = request.json.get('password')
                        # pas = password.encode('utf-8')
                        pas = base64.b64decode(password)
                        # print "password", pas
                        if api_key is None or secret_key == "" or Sid is None:
                            return jsonify({"response": "Invalid Credentials"})
                        else:
                            key_verf = models.api_vald(api_key=api_key, secret_key=secret_key)
                            if key_verf == "Api key Verified":
                                # Sid = uuid.UUID(sid)
                                # user = models.mydb.User.find_one({"SID" : Sid}, {"_id":0})
                                if Sid == session.sid:
                                    #change session.sid to lst id used of or updated id.

                                    # otp_stat = user['OTP_Verf']
                                    # if otp_stat == 'Verified':
                                    key = "\xd4\xe6\x1a\x83\x1d\xf7\xa43\xf0\xe3)j\x06\xa7/\xba"
                                    IV = "Q\xb9\x11mk\x08*\xd1\n4N\x13\x05n\xc4^"
                                    cipher_suit = AES.new(key, AES.MODE_CFB, IV)
                                    # print "before", pas
                                    # pas = str(password)
                                    dec_pas = cipher_suit.decrypt(pas)
                                    # dd = dec_pas.decode('ascii')
                                    # print "after", dec_pas
                                    # dec_pas = password.decode('hex')
                                    session.clear()
                                    return models.add_password(sid = Sid, password = dec_pas)
                                    # else:
                                    #     return jsonify({"response": "Your OTP is not verified"})
                                else:
                                    return jsonify({"response": "Session Id mismatch"})
                            else:
                                return jsonify({"response": key_Verf})
                    else:
                        return jsonify({"response": "Incomplete JSON data"})
                else:
                    return jsonify({"response": "OTP not Verified. Please Verify before proceding further."})
            else:
                print "session Expired. Recreating session..."
                new_session = models.recreate_session(Sid)
                return new_session
                # models.mydb.sessions.update({"sid" : session.sid}, {"$set": {"Last Used" : datetime.now()}})
        else:
            return jsonify({"response": "Invalid Credentials"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
