from flask import Flask, jsonify, request
import models
import json

def active():
    try:
        received_key = request.args.get('activation_key')
        link_verf = models.mydb.Activation.find_one({"activation_link" : received_key}, {"_id":0})
        if link_verf:
            link_verf1 = models.mydb.Activation.find_one({"activation_link" : received_key})
            email = link_verf1['email']
            client = link_verf1['Client Name']
            models.mydb.User.update({"Client Name" : client, "email" : email}, {"$set": {"Account" : "Active"}})
            # remove the entry for active Account.
            # models.mydb.Activation.remove( { "email" : email }, 1 )
            return "Activation Successful"
        else:
            return "Activation Failed. Activation link does not match"
    except Exception as e:
        return "Error Occured: {}".format (str(e))
