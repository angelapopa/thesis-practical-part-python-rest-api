import joblib
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import RadiusNeighborsClassifier

from .estimate_rating_exception import EstimateRatingException

from flask import jsonify


def estimate_rating_knn(country, floor_area, total_energy, totalEnergyFieldName):
    # load classifier from file
    filename = "serialized_knn_classifier_" + country + ".pck"

    parentDirPath = os.path.split(os.path.split(os.path.abspath(__file__))[
        0])[0]
    filepath = os.path.join(
        parentDirPath, "trained_models", "knn", country, filename)
    print("Importing " + filepath)

    try:
        knn_classifier = joblib.load(filepath)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No trained classifier was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)
    except:
        return jsonify("Something else went wrong")

    # load scaler from file
    filename2 = "serialized_knn_scaler_" + country + ".pck"
    filepath2 = os.path.join(
        parentDirPath, "trained_models", "knn", country, filename2)

    try:
        knn_scaler = joblib.load(filepath2)
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

    new_X = knn_scaler.transform(new_X)

    y_pred_knn_for_one = knn_classifier.predict(new_X)

    print("knn prediction for one")
    print(y_pred_knn_for_one)

    # Warning Regarding the Nearest Neighbors algorithms,
    # if two neighbors  and  have identical distances but different labels, the result will depend on the ordering of the training data.
    knn_neighbors = knn_classifier.kneighbors(new_X)

    print("knn neighbors")
    print("The closest neighbors are ([distance, row_index])")
    print(knn_neighbors)

    # load original df from file
    filename2 = "serialized_knn_dataframe_" + country + ".pck"
    filepath2 = os.path.join(
        parentDirPath, "trained_models", "knn", country, filename2)

    try:
        knn_dataframe = joblib.load(filepath2)
    except FileNotFoundError:
        ex = EstimateRatingException(
            "No Serialized dataframe was found for " + country.capitalize() + "!")
        # throwing exception is not working well when needing the message out of the exception
        # raise ex
        return jsonify(ex.message)

    neigbors = []
    nr_of_neighbours = len(knn_neighbors)

    # radius_dataframe is the data from DB saved in a file :(
    for i in range(0, nr_of_neighbours):
        # print("row_index of the original df")
        # print(radius_neighbors[1][0][i])
        # print(radius_dataframe.iloc[radius_neighbors[1][0][i], :])

        # extract each field
        element = {}
        element['rating'] = knn_dataframe.iloc[knn_neighbors[1][0][i], 1]
        element['totalFloorArea'] = str(
            knn_dataframe.iloc[knn_neighbors[1][0][i], 2])
        element['finalEnergyDemand'] = str(
            knn_dataframe.iloc[knn_neighbors[1][0][i], 3])
        neigbors.append(element)

    result = {}
    result['estimated-rating'] = y_pred_knn_for_one[0]
    result['neighbors'] = neigbors
    return result
