from flask import Flask, jsonify, request, session
from datetime import timedelta, datetime
import SendActivationApi
import models
import uuid
import json

def valid_api():
    try:
        if 'apiKey' in request.json:
            api_key = request.json.get('apiKey')
            if 'secretkey' in request.json and 'email' in request.json and 'phone' in request.json:
                secret_key = request.json.get('secretkey')
                email = request.json.get('email')
                phone = request.json.get('phone')
                if api_key == "" or secret_key == "":
                    return jsonify({"error-message": "Invalid Credentials"})
                else:
                    key_verf = models.api_vald(api_key=api_key, secret_key=secret_key)
                    if key_verf == "Api key Verified":
                        api_auth = models.mydb.Os_ver.find_one({"api_key" : api_key})
                        client = api_auth['client']
                        # sid = uuid.uuid4()
                        # session['sid'] = sid
                        session['client'] = client
                        session['user'] = email
                        session['Reg_Phase'] = "Phase 1 started."
                        entry = models.create_user(email = email, phone = phone, client = client)
                        if entry == "Please fill all the feilds carefully":
                            return jsonify({"error-message": entry})
                        else:
                            if entry == "Email or Phone already exists.":
                                return jsonify({"error-message": entry})
                            else:
                                # addd client also
                                session['Account'] = "Inactive"
                                mail = SendActivationApi.mailer(sid=session.sid, Resend="False")
                                if mail == "Mail Sent Successfully":
                                    # sent_at = datetime.now() + timedelta(minutes=2)
                                    # models.mydb.User.update({"Client Name" : client, "email" : email}, {"$set": {"sent_at" : sent_at}})
                                    # session['sent_at'] = sent_at
                                    session['Reg_Phase'] = "phase 1 complete"
                                    # if otp resend then having issue with sent_at timmings
                                    return jsonify({'Session_id' : entry, 'error-message' : mail})
                                else:
                                    session['sent_at'] = "Mail sending Failed"
                                    session['Reg_Phase'] = "Mail sending Failed"
                                    return jsonify({'Session_id' : entry, 'error-message' : "Mail sending Failed"})
                        # models.mydb.sessions.update({"sid" : session.sid}, {"$set": {"Last Used" : datetime.now()}})
                    else:
                        return jsonify({"error-message": "Invalid Api Key"})

            else:
                # raise ValueError ('Incomplete JSON data')
                return jsonify({"error-message": "Incomplete JSON data"})
        else:
            # raise ValueError ('Invalid Argument List')
            return jsonify({"error-message": "Invalid Credentials"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
