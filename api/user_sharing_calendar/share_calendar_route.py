from flask import jsonify, request
from flasgger import swag_from

from api.user_sharing_calendar.share_calendar import( remove_calendar_share, 
retrieve_subscriptions, 
subscribe_user_to_calendar,
get_shared_calendars_by_me,
get_my_shared_calendars,
unsubscribe_user_from_calendar, update_sharing_level)






def setup_user_share_calendars_routes(app):
    @app.route('/subscribe', methods=['POST'])
    def subscribe_to_calendar():
        input_data = request.json

        if 'user_id' not in input_data or 'calendar_id' not in input_data:
            return jsonify({'status': 'Error', 'message': 'user_id and calendar_id are required'}), 422

        user_id = input_data['user_id']
        calendar_id = input_data['calendar_id']

        subscribe_result = subscribe_user_to_calendar(user_id, calendar_id)

        if subscribe_result:
            return jsonify({'status': 'Success', 'message': 'Subscribed to the calendar'}), 200
        else:
            return jsonify({'status': 'Error', 'message': 'Failed to subscribe to the calendar'}), 500

    @app.route('/unsubscribe', methods=['POST'])
    @swag_from('apidocs/unsubscribe_calendar.yml')
    def unsubscribe_from_calendar():
        input_data = request.json

        if 'user_id' not in input_data or 'calendar_id' not in input_data:
            return jsonify({'status': 'Error', 'message': 'user_id and calendar_id are required'}), 422

        user_id = input_data['user_id']
        calendar_id = input_data['calendar_id']

        unsubscribe_result = unsubscribe_user_from_calendar(user_id, calendar_id)

        if unsubscribe_result:
            return jsonify({'status': 'Success', 'message': 'Unsubscribed from the calendar'}), 200
        else:
            return jsonify({'status': 'Error', 'message': 'Failed to unsubscribe from the calendar'}), 500

    @app.route('/user/subscriptions', methods=['GET'])
    @swag_from('apidocs/list_user_subscription.yml')
    def list_subscriptions():
        user_id = request.args.get('user_id')

        subscriptions = retrieve_subscriptions(user_id)

        response = {
            "user_id": user_id,
            "subscriptions": subscriptions
        }

        return jsonify(response)

    @app.route('/user/subscriptions/authorized', methods=['GET'])
    @swag_from('apidocs/list_authorized_user_subscriptions.yml')
    def list_subscriptions_authorized():
        user_id = request.args.get('user_id')

        subscriptions = retrieve_subscriptions(user_id)

        response = {
            "user_id": user_id,
            "subscriptions": subscriptions
        }

        return jsonify(response)

    @app.route('/user/shared-calendars-by-me/<user_id>', methods=['GET'])
    def get_shared_calendars_by_me_route(user_id):
        shared_calendars = get_shared_calendars_by_me(user_id)
        return jsonify(shared_calendars)

    @app.route('/update-sharing-level', methods=['PUT'])
    def update_sharing_level_route():
        data = request.get_json()
        user_id = data.get('user_id')
        calendar_id = data.get('calendar_id')
        new_access_level = data.get('access_level')

        result = update_sharing_level(user_id, calendar_id, new_access_level)

        return jsonify(result)

    @app.route('/my-shared-calendars', methods=['GET'])
    def get_my_shared_calendars_route():
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        user_id = request.args.get('user_id', '')
        search_phrase = request.args.get('search_phrase', '')

        result= get_my_shared_calendars(page, per_page, user_id, search_phrase)

        return jsonify(result),  

    @app.route('/remove-calendar-share', methods=['DELETE'])
    def remove_calendar_share_route():
        data = request.get_json()
        user_id = data.get('user_id')
        calendar_id = data.get('calendar_id')

        result = remove_calendar_share(user_id, calendar_id)

        return jsonify(result)