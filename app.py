from flask import Flask, request, jsonify, redirect, session, app
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from datetime import datetime, timedelta
from pymongo import MongoClient
import AccountActivationApi
from bson import json_util
import SendActivationApi
import IotEndpointApi
import OnBoardingApi
import UserState
import Reg_final
import LoginApi
import Reg_init
import Reg_mid
import IotApi
import models
import LogoutApi
import json
import uuid


DEBUG = True
HOST = '0.0.0.0'
PORT = 8000

class MongoSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None):
        CallbackDict.__init__(self, initial)
        self.sid = sid
        self.modified = False


class MongoSessionInterface(SessionInterface):

    def __init__(self, host='localhost', port=27017,
                 db='', collection='sessions'):
        client = MongoClient(host, port)
        self.store = client[db][collection]

    def open_session(self, app, request):
        try:
            sid = request.cookies.get(app.session_cookie_name)
            sid1 = str(uuid.uuid4())
            if sid:
                stored_session = self.store.find_one({'sid': sid})
                if stored_session:
                    if datetime.now() - stored_session.get('Last Used') > timedelta(minutes=20):

                        return MongoSession(sid=sid1)
                    else:
                        return MongoSession(initial=stored_session['data'],
                                            sid=stored_session['sid'])

            return MongoSession(sid=sid1)
        except Exception as e:
            return "Error Occured: {}".format (str(e))

    def save_session(self, app, session, response):
        try:
            domain = self.get_cookie_domain(app)
            if not session:
                response.delete_cookie(app.session_cookie_name, domain=domain)
                return
            if self.get_expiration_time(app, session):
                Last_Used = self.get_expiration_time(app, session)
            else:
                Last_Used = datetime.now()

            self.store.update({'sid': session.sid},
                              {'sid': session.sid,
                               'data': session,
                               'Last Used': Last_Used}, True)
            response.set_cookie(app.session_cookie_name, session.sid,
                                expires=self.get_expiration_time(app, session),
                                httponly=True, domain=domain)
        except Exception as e:
            return "Error Occured: {}".format (str(e))


app = Flask(__name__)
app.session_interface = MongoSessionInterface(db='IOT_database_New')
app.secret_key = 'F12Zrkj545s47j\3yX RasjH!jmM]Lwf/,?KT'




@app.route('/')
def Hello():
    return "Welcome to IoT Workshop"


@app.route('/api1.0/onboarding', methods=['POST'])
def on_boarding():
    try:
        return OnBoardingApi.gen_api()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/userstate', methods=["POST"])
def userState():
    try:
        return UserState.user_state()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/reg1', methods=["POST"])
def register():
    try:
        return Reg_init.valid_api()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/reg2', methods=["POST"])
def register2():
    try:
        return Reg_mid.valid_otp()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/reg3', methods=["POST"])
def register3():
    try:
        return Reg_final.password()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/send_activation', methods=('GET',"POST"))
def active_link():
    try:
        if 'sid' in request.json:
            Sid = request.json.get('sid')
            mailsnd = SendActivationApi.mailer(sid = Sid)
            return mailsnd
        else:
            return jsonify({"response": "Argument missing"})
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/activation', methods=('GET',"POST"))
def activation():
    try:
        return AccountActivationApi.active()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/login', methods=('GET', "POST"))
def login():
    try:
        return LoginApi.user_login()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/logout', methods=('GET', "POST"))
def logout():
    try:
        print "idhr aaya"
        return LogoutApi.usr_logout()
        print "idhr ni aaya"
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/iot_api', methods=["POST"])
def IOT_Api():
    try:
        return IotApi.iot_api()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


@app.route('/api1.0/iot_endpoint', methods=["GET"])
def Endpoint_api():
    try:
        return IotEndpointApi.endpoint()
    except Exception as e:
        return "Error Occured: {}".format (str(e))


if __name__ == '__main__':
    app.run(debug=DEBUG, host=HOST, port=PORT)
