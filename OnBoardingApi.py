from flask_bcrypt import generate_password_hash
from flask import Flask, jsonify, request
import models
import json


def gen_api():
    try:
        if 'client' in request.json:
            client = request.json.get('client')
            if client == "":
                return jsonify({"response": "Please fill a valid Client Name"})
            else:
                Gen_key = models.apikey_auth(client)
                if Gen_key == 'Client Already Exists':
                    return jsonify({"response": "Client Already Exists"})
                else:
                    return Gen_key
        else:
            return jsonify({"response": "Invalid Client"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
