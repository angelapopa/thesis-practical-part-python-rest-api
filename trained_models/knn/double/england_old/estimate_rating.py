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
    if 'country' in request.args:
        country = request.args['country'].lower()
    else:
        return jsonify("No country field provided. Please specify a country.")

    if 'floor_area' in request.args:
        floor_area = int(request.args['floor_area'])
    else:
        return jsonify("No floor_area field provided. Please specify a floor_area.")

    if 'total_energy' in request.args:
        total_energy = int(request.args['total_energy'])
    else:
        return jsonify("No total_energy field provided. Please specify a total_energy.")

    # joblib - load model from file
    filename = "serialized_joblib_model_" + country + ".pck"

    parentDirPath = os.path.split(os.path.split(os.path.abspath(__file__))[
        0])[0]
    filepath = os.path.join(
        parentDirPath, "trained_models" + os.path.sep + "knn" + os.path.sep + country + os.path.sep + filename)
    print("Importing " + filepath)

    try:
        loaded_model = joblib.load(filepath)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No trained model was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)
    except:
        return jsonify("Something else went wrong")

    new_data_rows = [[floor_area, total_energy]]
    print("["+str(floor_area) + ", " + str(total_energy) + "]")

    new_data_df = pd.DataFrame(
        new_data_rows, columns=['ratedDwelling_spatialData_totalFloorArea_value', 'ratedDwelling_thermalData_finalEnergyDemand_value'])
    print(new_data_df.head())

    new_X = new_data_df

    print("the dwelling that should be rated is:")
    print(new_X)

    filename2 = "serialized_joblib_scaler_" + country + ".pck"
    filepath2 = os.path.join(
        parentDirPath, "trained_models" + os.path.sep + "knn" + os.path.sep + country + os.path.sep + filename2)

    try:
        scaler = joblib.load(filepath2)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No Scaler was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)

    new_X = scaler.transform(new_X)

    # result_load = loaded_model.score(X_test, y_test)
    # print("accuracy score from loaded model")
    # print(result_load)

    new_pred = loaded_model.predict(new_X)
    print("new prediction")
    print(new_pred)

    filename3 = "serialized_joblib_radius_classifier_" + country + ".pck"

    filepath3 = os.path.join(
        parentDirPath, "trained_models" + os.path.sep + "knn" + os.path.sep + country + os.path.sep + filename3)

    try:
        radius_classifier = RadiusNeighborsClassifier(joblib.load(filepath3))
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No Radius Classifier was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)

    y_pred_radius_for_one = radius_classifier.predict(new_X)

    print("radius prediction for one")
    print(y_pred_radius_for_one)

    radius_neighbors = radius_classifier.radius_neighbors(X=new_X, return_distance=True,
                                                          sort_results=True)

    print("radius neighbors")
    print("The closest neighbors are ([distance, row_index])")
    print(radius_neighbors)

# data_df is the data from db :(
#    for i in range(0, 3):
#        print(data_df.iloc[radius_neighbors[1][0][i], :])

    # return a json object
    return jsonify(new_pred[0])


@ app.errorhandler(404)
def page_not_found(e):
    print("we entered page not found")
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
