from flask import jsonify, request
from flasgger import swag_from
from api.user_calendars.user_calendars import retrieve_linked_calendars, delete_calendar_source

def setup_user_calendars_routes(app):
    @app.route('/user/calendars', methods=['GET'])
    @swag_from('/api/user_calendars/apidocs/link_calendar.yml')
    def get_linked_calendars():
        user_id = request.args.get('user_id')

        # Retrieve linked calendars based on user_id
        linked_calendars = retrieve_linked_calendars(user_id)

        # Format the response
        metadata = {
            "page": 1,
            "per_page": 20,
            "page_count": 20,
            "total_count": len(linked_calendars),
            "links": [
                {"self": f"/user/calendars?page=1&per_page=20"},
                {"first": f"/user/calendars?page=1&per_page=20"},
                {"previous": ""},
                {"next": f"/user/calendars?page=2&per_page=20"},
                {"last": f"/user/calendars?page=2&per_page=20"}
            ]
        }

        records = [{"id": calendar.id, "name": calendar.display_name, "type": calendar.source_type_id} for calendar in linked_calendars]

        response = {
            "_metadata": metadata,
            "records": records
        }

        return jsonify(response)

    # Create API endpoint for unlinking a calendar
    @app.route('/user/calendars/unlink', methods=['POST'])
    @swag_from('/api/user_calendars/apidocs/unlink_calendar.yml')  
    def unlink_calendar():
        input_data = request.json

        if 'user_id' not in input_data or 'calendar_id' not in input_data:
            return jsonify({'status': 'Error', 'message': 'user_id and calendar_id are required'}), 422

        user_id = input_data['user_id']
        calendar_id = input_data['calendar_id']

        # Delete the calendar source based on user_id and calendar_id
        delete_calendar_source(user_id, calendar_id)

        return jsonify({'status': 'Success', 'message': 'Calendar unlinked successfully'}), 200
