
import joblib
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler

print("we entered the estimate method.")

# joblib - load model from file
filename = "serialized_joblib_model_england.pck"

parentDirPath = os.path.split(os.path.split(os.path.abspath(__file__))[
    0])[0]
filepath = os.path.join(
    parentDirPath, "trained_models" + os.path.sep + "knn" + os.path.sep + "england" + os.path.sep + filename)
print("Importing " + filepath)

loaded_model = joblib.load(filepath)

floor_area = 387
total_energy = 381
new_data_rows = [[floor_area, total_energy]]

new_data_df = pd.DataFrame(
    new_data_rows, columns=['ratedDwelling_spatialData_totalFloorArea_value', 'ratedDwelling_thermalData_finalEnergyDemand_value'])
print(new_data_df.head())

new_X = new_data_df

print("the dwelling that should be rated is:")
print(new_X)

filename2 = "serialized_joblib_scaler_england.pck"
filepath2 = os.path.join(
    parentDirPath, "trained_models"+os.path.sep + "knn"+os.path.sep + "england" + os.path.sep + filename2)
scaler = joblib.load(filepath2)
new_X = scaler.transform(new_X)

# result_load = loaded_model.score(X_test, y_test)
# print("accuracy score from loaded model")
# print(result_load)

new_pred = loaded_model.predict(new_X)
print("new prediction")
print(new_pred)
print(new_pred[0])
