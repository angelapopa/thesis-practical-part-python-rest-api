import flask
import joblib
import os
from flask import request, jsonify
from flask_cors import CORS

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# with default arguments in order to allow CORS for all domains on all routes
# CORS(app)
cors = CORS(app, resources={
            r"/api/*": {"origins": {"https://epc-modelling-app.herokuapp.com", "http://localhost:3000"}}})


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

    # joblib - load model from file
    filename = "serialized_joblib_model_england.pck"

    parentDirPath = os.path.split(os.path.split(os.path.abspath(__file__))[
        0])[0]
    filepath = os.path.join(
        parentDirPath, "trained_models\\knn\\england\\" + filename)
    print("Importing " + filepath)

    loaded_model = joblib.load(filepath)

    new_data_rows = [[floor_area, total_energy]]
    print("["+floor_area + ", " + total_energy + "]")

    new_data_df = pd.DataFrame(
        new_data_rows, columns=['ratedDwelling_spatialData_totalFloorArea_value', 'ratedDwelling_thermalData_finalEnergyDemand_value'])
    print(new_data_df.head())

    new_X = new_data_df

    print("the dwelling that should be rated is:")
    print(new_X)

    filename2 = "serialized_joblib_scaler_england.pck"
    filepath2 = os.path.join(
        parentDirPath, "trained_models\\knn\\england\\" + filename2)
    scaler = joblib.load(filepath2)
    new_X = scaler.transform(new_X)

    # result_load = loaded_model.score(X_test, y_test)
    # print("accuracy score from loaded model")
    # print(result_load)

    new_pred = loaded_model.predict(new_X)
    print("new prediction")
    print(new_pred)


return jsonify(new_pred)


@ app.errorhandler(404)
def page_not_found(e):
    print("we entered page not found")
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
