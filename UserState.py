from flask import Flask, jsonify, request, Response
from bson import json_util
import models
import json


def user_state():
    try:
        if 'apiKey' in request.json and 'secretkey' in request.json and 'email' in request.json:
            api_key = request.json.get('apiKey')
            secret_key = request.json.get('secretkey')
            email = request.json.get('email')
            if api_key is None:
                return jsonify({"response": "Invalid Credentials"})
            else:
                key_verf = models.api_vald(api_key=api_key, secret_key=secret_key)
                if key_verf == "Api key Verified":
                    api_auth = models.mydb.Os_ver.find_one({"api_key" : api_key})
                    client = api_auth['client']
                    user = models.mydb.User.find_one({"Client Name" : client, "email" : email}, {"_id":0})
                    if user:
                        acc_stat = user['Account']
                        otp_stat = user['OTP_Verf']
                        client = user['Client Name']
                        phone = user['phone']
                        login_status = user['logged_in']
                        return jsonify({"User": email, "Phone" : phone, "User Client" : client, "Account Status" : acc_stat, "OTP Status" : otp_stat, "Logged In" : login_status})
                    else:
                        return jsonify({"response": "User Not Found"})
                else:
                    return jsonify({"response": key_Verf})
        else:
            return jsonify({"response": "InComplete Json Data"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
