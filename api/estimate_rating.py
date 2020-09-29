import flask
from flask import request, jsonify
from flask_cors import CORS

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# with default arguments in order to allow CORS for all domains on all routes
# CORS(app)
cors = CORS(app, resources={
            r"/api/*": {"origins": {"https://epc-modelling-app.herokuapp.com/", "http://localhost:3000"}}})


@ app.route('/api/estimate', methods=['GET'])
def api_estimate():
    print("we entered the estimate method.")
    # Check if floor_area and total_energy were provided as part of the URL.
    if 'floor_area' in request.args:
        floor_area = int(request.args['floor_area'])
    else:
        return "Error: No floor_area field provided. Please specify a floor_area."

    if 'total_energy' in request.args:
        total_energy = int(request.args['total_energy'])
    else:
        return "Error: No total_energy field provided. Please specify a total_energy."

    # some test data
    estimated_data = [
        {'id': 0,
         'rating': 'C',
         'neighbours': 'no neighbours yet',
         'input_floor_area': floor_area,
         'input_total_energy': total_energy}, {'id': 1, 'somestuff': 5}
    ]
    print(estimated_data)
    return jsonify(estimated_data)


@ app.errorhandler(404)
def page_not_found(e):
    print("we entered page not found")
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
