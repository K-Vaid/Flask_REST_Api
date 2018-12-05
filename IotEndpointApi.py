from flask import Flask, jsonify, request, Response
from bson import json_util
import models
import json

def endpoint():
    try:
        if 'apiKey' in request.args and 'phone_number' in request.args:
            api_key = request.args.get('apiKey')
            if api_key is None:
                return jsonify({"response": "Invalid Credentials"})
            else:
                try:
                    key_verf = models.api_vald(api_key)
                    if key_verf == "Api key Verified":
                        phone = request.args.get('phone_number')
                        exists = models.mydb.Data.find_one({"phone_no" : phone}, {"_id":0})
                        if exists:
                            if 'date' in request.args:
                                # date = request.args.get('date')
                                # if date == "all":
                                user_no = models.mydb.Data.find({"phone_no" : phone})
                                data_list = []
                                for data_entry in user_no:
                                    user_data = data_entry['data']
                                    data_list.append(user_data)
                                return Response(json_util.dumps(data_list))
                                # else:
                                #     return jsonify({"response": "Sorry, No data found."})
                            else:
                                user_no = models.mydb.Data.find({"phone_no" : phone})
                                for data_entry in user_no:
                                    latest = data_entry
                                user_data = latest['data']
                                return Response(json_util.dumps(user_data))
                        else:
                            return jsonify({"response": "Sorry, No data found."})
                    else:
                        return jsonify({"response": key_Verf})
                except Exception as e:
                    return "Error Occured: {}".format (str(e))
        else:
            raise ValueError ('Invalid Argument List')
    except Exception as e:
        return "Error Occured: {}".format (str(e))
