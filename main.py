# from data_processing.load_data_train_test_val import load_train_test_val, load_to_predict
# from prediction.predict_activities import analyze_file
# import tensorflow as tf
#
# window_size = 150
# overlap = 75
# dir_path_train = 'data/train'
# dir_path_test = 'data/test'
#
# # splot train dataset into train and val
# # trainX, trainy, testX, testy, valX, valy = load_train_test_val(dir_path_train, dir_path_test, window_size, overlap, val_split=0.1)
#
#
# file_path = 'data/test/przemek_2.xlsx'
#
# model = tf.keras.models.load_model('saved_models/LSTM_w150_o75_e100_p33')
#
# # act, activities, end_times, durations = analyze_file(file_path, window_size, overlap, model, True)
import sqlite3
conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type = 'table';")
files = cursor.fetchall()
print(files)
conn.close()
