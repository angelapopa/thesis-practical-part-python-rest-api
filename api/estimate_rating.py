import flask
from flask import request, jsonify
from flask_cors import CORS

import joblib
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import RadiusNeighborsClassifier

from .estimate_rating_exception import EstimateRatingException

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

    # load classifier from file
    filename = "serialized_radius_classifier_" + country + ".pck"

    parentDirPath = os.path.split(os.path.split(os.path.abspath(__file__))[
        0])[0]
    filepath = os.path.join(
        parentDirPath, "trained_models", "knn", country, filename)
    print("Importing " + filepath)

    try:
        radius_classifier = joblib.load(filepath)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No trained classifier was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)
    except:
        return jsonify("Something else went wrong")

    # load scaler from file
    filename2 = "serialized_radius_scaler_" + country + ".pck"
    filepath2 = os.path.join(
        parentDirPath, "trained_models", "knn", country, filename2)

    try:
        radius_scaler = joblib.load(filepath2)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No Scaler was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)

    new_data_rows = [[floor_area, total_energy]]
    print("["+str(floor_area) + ", " + str(total_energy) + "]")

    # energy db column name
    columnEnergy = 'ratedDwelling_thermalData_' + totalEnergyFieldName + '_value'

    new_data_df = pd.DataFrame(
        new_data_rows, columns=['ratedDwelling_spatialData_totalFloorArea_value', columnEnergy])
    print(new_data_df.head())

    new_X = new_data_df

    print("the dwelling that should be rated is:")
    print(new_X)

    new_X = radius_scaler.transform(new_X)

    y_pred_radius_for_one = radius_classifier.predict(new_X)

    print("radius prediction for one")
    print(y_pred_radius_for_one)

    radius_neighbors = radius_classifier.radius_neighbors(X=new_X, return_distance=True,
                                                          sort_results=True)

    print("radius neighbors")
    print("The closest neighbors are ([distance, row_index])")
    print(radius_neighbors)

    # load original df from file
    filename2 = "serialized_radius_dataframe_" + country + ".pck"
    filepath2 = os.path.join(
        parentDirPath, "trained_models", "knn", country, filename2)

    try:
        radius_dataframe = joblib.load(filepath2)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No Serialized dataframe was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)

    neigbors = []
    nr_of_neighbours = 5

    # radius_dataframe is the data from DB saved in a file :(
    for i in range(0, nr_of_neighbours):
        # print("row_index of the original df")
        # print(radius_neighbors[1][0][i])
        # print(radius_dataframe.iloc[radius_neighbors[1][0][i], :])

        # extract each field
        element = {}
        element['rating'] = radius_dataframe.iloc[radius_neighbors[1][0][i], 1]
        element['totalFloorArea'] = radius_dataframe.iloc[radius_neighbors[1][0][i], 2]
        element['finalEnergyDemand'] = radius_dataframe.iloc[radius_neighbors[1][0][i], 3]
        neigbors.append(element)

    result = {}
    result['estimated-rating'] = y_pred_radius_for_one[0]
    result['neighbors'] = neigbors

    return jsonify(result)


@ app.errorhandler(404)
def page_not_found(e):
    print("we entered page not found")
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
