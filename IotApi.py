from flask import Flask, jsonify, request
from bson import json_util
import datetime
import models
import json

def iot_api():
    try:
        if 'apiKey' in request.args:
            api_key = request.args.get('apiKey')
            if api_key is None:
                return jsonify({"response": "Invalid Credentials"})
            else:
                try:
                    api_auth = models.mydb.Os_ver.find_one({"api_key" : api_key}, {"_id":0})
                    if api_auth:
                        if request.json == None:
                            return jsonify({"response": "Invalid Data"})
                        else:
                            try:
                                if 'phone_number' in request.json:
                                    phone_no = request.json.get('phone_number')
                                    json_data = request.get_json()
                                    timer = str(datetime.datetime.now())
                                    json_data['Received_at'] = timer
                                    return models.add_data(phone_no=phone_no, data=json_data)
                                else:
                                    raise ValueError ("Phone Number not found")
                            except Exception as e:
                                return "Error Occured: {}".format (str(e))
                    else:
                        return jsonify({"response": "Invalid Credentials"})
                except Exception as e:
                    return "Error Occured: {}".format (str(e))
        else:
            raise ValueError ('Invalid Argument List')
    except Exception as e:
        return "Error Occured: {}".format (str(e))
