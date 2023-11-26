 # api/search_invitees/search_invitees_routes.py
from flask import jsonify, request,Flask
from flasgger import swag_from
from api.search_invitees.search_invitees import search_invitees
from flasgger import Swagger

app = Flask(__name__)
Swagger(app)
def setup_search_invitees_routes(app):
    @app.route('/search', methods=['POST'])
    @swag_from('search_invitees.yml')  # Updated path
    def search_invitees_route():
        input_data = request.json

        if 'search_phrase' not in input_data:
            return jsonify({'status': 'Error', 'message': 'search_phrase is required'}), 422

        search_phrase = input_data['search_phrase']
        results = search_invitees(search_phrase)

        return jsonify(results)
