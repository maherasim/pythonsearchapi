# api/two_factor_auth/two_factor_auth_routes.py

from flask import jsonify, request
from flasgger import swag_from
from api.two_factor_auth.two_factor_auth import send_2fa_code, confirm_2fa_code
 
def setup_two_factor_auth_routes(app):
    @app.route('/send-2fa-code', methods=['POST'])
    @swag_from('/api/two_factor_auth/apidocs/send_2fa_code.yml')
    def send_2fa_code_route():
        input_data = request.json

        if 'email' not in input_data:
            return jsonify({'status': 'Error', 'message': 'email is required'}), 422

        email = input_data['email']
        return send_2fa_code(email)

    @app.route('/confirm-2fa-code', methods=['POST'])
    @swag_from('/api/two_factor_auth/apidocs/confirm_2fa_code.yml')
    def confirm_2fa_code_route():
        input_data = request.json

        if 'email' not in input_data or 'code' not in input_data:
            return jsonify({'status': 'Error', 'message': 'email and code are required'}), 422

        email = input_data['email']
        code = input_data['code']
        return confirm_2fa_code(email, code)
