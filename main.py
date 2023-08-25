from flask import Flask, request, jsonify
from model import User, db
from sqlalchemy.dialects.mysql import mysqlconnector
import mysql.connector

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://admin:Fire12345@pinng-dev.cmyva7x3ctnc.ap-southeast-2.rds.amazonaws.com:3306/dev'
db.init_app(app)


db.dialect = mysqlconnector.dialect()


app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'DBAPI': mysql.connector.connect}}

@app.route('/search-invitees', methods=['POST'])
def search_invitees():
    input_data = request.json

    if 'search_phrase' not in input_data:
        return jsonify({'status': 'Error', 'message': 'search_phrase is required'}), 422

    search_phrase = input_data['search_phrase']

   
    matched_users = User.query.filter(User.email.like(f"%{search_phrase}%") |
                                      User.name.like(f"%{search_phrase}%")).all()

    results = {user.email: user.name for user in matched_users}

    return jsonify(results)

if __name__ == '__main__':
    app.run()


