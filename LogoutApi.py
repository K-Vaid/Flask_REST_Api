from flask import Flask, jsonify, request,session
from bson import json_util
import models
import json

def usr_logout():
    try:
        if 'sid' in request.json:
            Sid = request.json.get('sid')
            if Sid != "":
                if 'login Status' in session and session['login Status'] == "True":
                    session['login Status'] = "False"
                    session['final stat'] = "logged out"
                    print "yaha se kiya....", session['login Status']
                    login_state = models.mydb.User.update({"Client Name" : session['Client'], "email" : session['User']}, {"$set": {"logged_in" : session['login Status']}})
                    session.clear()
                    return jsonify({"response": "Logged Out Successfully"})
                else:
                    user = models.mydb.User.find_one({"Current SID" : Sid})
                    if user:
                        session['login Status'] = "False"
                        models.mydb.User.update({"Current SID" : Sid}, {"$set": {"logged_in" : session['login Status']}})
                        print "yaha se kiya returns....", session['login Status']
                        session.clear()
                        return jsonify({"response": "Logged Out Successfully"})
            else:
                return jsonify({"response": "Invalid Session Id"})
        else:
            return jsonify({"response": "Incomplete JSON data"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))
