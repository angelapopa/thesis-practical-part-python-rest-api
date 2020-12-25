import flask
from flask import request, jsonify
from flask_cors import CORS

from .estimate_rating_radius import estimate_rating_radius

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# with default arguments in order to allow CORS for all domains on all routes
# CORS(app)
cors = CORS(app, resources={
            r"/api/*": {"origins": {"https://epc-modelling-app.herokuapp.com", "http://localhost:3000"}}})


@ app.route('/api/estimate-rating', methods=['GET'])
def api_estimate_rating():
    print("we entered the estimate rating method.")
    # Check if needed params were provided as part of the URL.
    if 'energy_prop' in request.args:
        totalEnergyFieldName = request.args['energy_prop']
    else:
        return jsonify("No energy field name was provided. Please specify the name of the energy field.")

    if 'country' in request.args:
        country = request.args['country'].lower()
    else:
        return jsonify("No country field provided. Please specify a country.")

    if 'floor_area' in request.args:
        floor_area = int(float(request.args['floor_area']))
    else:
        return jsonify("No floor_area field provided. Please specify a floor_area.")

    if 'total_energy' in request.args:
        total_energy = int(float(request.args['total_energy']))
    else:
        return jsonify("No total_energy field provided. Please specify a total_energy.")

    return jsonify(estimate_rating_radius(country, floor_area, total_energy, totalEnergyFieldName))


@ app.errorhandler(404)
def page_not_found(e):
    print("we entered page not found")
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
