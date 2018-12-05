from flask import Flask, jsonify, request, session
from datetime import timedelta, datetime
import models
import uuid
import json
import app

def valid_otp():
    try:
        if 'apiKey' in request.json and 'sid' in request.json:
            if 'Reg_Phase' in session and 'user' in session and 'client' in session and 'sent_at' in session:
                api_key = request.json.get('apiKey')
                Sid = request.json.get('sid')
                if session['Reg_Phase'] == "Mail sending Failed":
                    return jsonify({"response": "OTP sending Failed. Please Request another OTP to continue."})
                else:
                    if 'secretkey' in request.json and 'otp' in request.json:
                        secret_key = request.json.get('secretkey')
                        otp = request.json.get('otp')
                        if api_key is None or secret_key == "" or Sid == "":
                            return jsonify({"response": "Invalid Credentials"})
                        else:
                            key_verf = models.api_vald(api_key=api_key, secret_key=secret_key)
                            if key_verf == "Api key Verified":
                                # s_id = models.mydb.User.find_one({"SID" : Sid}, {"_id":0})
                                # print "Session....", session.sid
                                if Sid == session.sid:
                                    # can replace
                                    user = session['user']
                                    client = session['client']
                                    return otp_auth(user=user, client=client, otp=otp)
                                    # added client, not yet in database.
                                else:
                                    return jsonify({"response": "Session Id mismatch"})
                            else:
                                return jsonify({"response": key_Verf})
                    else:
                        return jsonify({"response": "Incomplete JSON data"})
            else:
                sid = request.json.get('sid')
                print "session Expired. Recreating session..."
                new_session = models.recreate_session(sid)
                return new_session
                # models.mydb.sessions.update({"sid" : session.sid}, {"$set": {"Last Used" : datetime.now()}})
        else:
            return jsonify({"response": "Invalid Credentials"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))


def otp_auth(user, client, otp):
    try:
        otp_record = models.mydb.Activation.find_one({"Client Name" : client, "email" : user}, {"_id":0})
        if otp_record:
            db_otp = otp_record['OTP']
            # Received_at = datetime.now() - session['sent_at']
            if session['sent_at'] < datetime.now():
                return jsonify({"response": "OTP Verification Failed. Time Out"})
            else:
                if otp == db_otp:
                    models.mydb.User.update({"Client Name" : client, "email" : user}, {"$set": {"OTP_Verf" : "Verified"}})
                    session['Reg_Phase'] = "OTP Verified"
                    session.pop('Account', None)
                    # models.mydb.User.update({"Client Name" : client, "email" : user}, {"$unset": {"sent_at"}})
                    return jsonify({'Session_id' : session.sid, "response": "OTP Verified"})
                else:
                    return jsonify({"response": "Invalid OTP"})
        else:
            return jsonify({"response": "No OTP for this user"})
        # models.mydb.sessions.update({"sid" : session.sid}, {"$set": {"Last Used" : datetime.now()}})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
