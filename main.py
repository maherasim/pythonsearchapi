# api/main.py
from flask import Flask
from flasgger import Swagger
from api.search_invitees.search_invitees_routes import setup_search_invitees_routes
from api.two_factor_auth.two_factor_auth_routes import setup_two_factor_auth_routes
from api.user_calendars.user_calendars_routes import setup_user_calendars_routes
from api.user_sharing_calendar.share_calendar_route import setup_user_share_calendars_routes
from model import db
import mysql.connector

app = Flask(__name__)
Swagger(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:Fire12345@pinng-dev.cmyva7x3ctnc.ap-southeast-2.rds.amazonaws.com:3306/dev'
db.init_app(app)
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'DBAPI': mysql.connector}}



# Set up routes
setup_search_invitees_routes(app)
setup_two_factor_auth_routes(app)
setup_user_calendars_routes(app)
setup_user_share_calendars_routes(app)

if __name__ == '__main__':
    app.run()