import hashlib
import logging
from logging.handlers import RotatingFileHandler
from web3 import Web3, HTTPProvider

from flask import Flask
from flask_jwt import JWT
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import safe_str_cmp


app = Flask(__name__, static_url_path="", static_folder="static")
app.config.from_object('crypto_predict.config.DevConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

handler = RotatingFileHandler('crypto_predict.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

db = SQLAlchemy(app)


w3 = Web3(HTTPProvider(app.config["RPC_PROVIDER"]))


#########################
# JWT Handler
#########################


from crypto_predict.models.user import UserModel


def authenticate(username, password):
    user = UserModel.query.filter_by(user_name=username).first()
    if user and safe_str_cmp(user.password.encode('utf-8'), hashlib.md5(str(password).encode('utf-8')).hexdigest()):
        return user


def identity(payload):
    user_id = payload['identity']
    return UserModel.query.filter_by(id=user_id).first()


jwt = JWT(app, authenticate, identity)


from crypto_predict.controllers import export_api_list
from crypto_predict.views import export_views_list

end_points = set(export_views_list).union(set(export_api_list))

for api in end_points:
    if hasattr(api, "url"):
        api_url = getattr(api, "url")
    else:
        api_url = api.__name__.lower().split("api")[0]
    api_name = api.__name__.lower()
    print (api_name, " -> ", "/{}".format(api_url))
    view = api.as_view("{}".format(api_name))
    app.add_url_rule(
        "/{}".format(api_url),
        view_func=view
    )
