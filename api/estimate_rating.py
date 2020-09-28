import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/api/estimate', methods=['GET'])
def api_estimate():

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
         'Rating': 'C',
         'neighbours': 'no neighbours yet',
         'input_floor_area': floor_area,
         'input_total_energy': total_energy}
    ]

    return jsonify(estimated_data)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
