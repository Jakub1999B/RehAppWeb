from __future__ import print_function
import pandas as pd
import seaborn as sns
from scipy import stats
# from IPython.display import display, HTML
from sklearn import metrics
from sklearn.metrics import classification_report
from sklearn import preprocessing
import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Reshape
from keras.layers import Conv2D, MaxPooling2D
# from keras.utils import np_utils
from numpy import mean
from numpy import std
from numpy import dstack
from pandas import read_csv
from keras.models import Sequential
from keras.utils import to_categorical
from matplotlib import pyplot
from keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout, LSTM
import tensorflow as tf
from scipy.signal import butter, filtfilt
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal


def sliding_windows(data, window_size, overlap):
    ind = 0
    windows = []
    for i in range(len(data)- window_size + 1):
        end = ind + window_size
        window = data[ind:end]
        windows.append(window)
        ind += overlap
        if ind > len(data)-overlap:
            break
    return windows

def plot_data(data):
    print(len(data))
    plt.figure(figsize=(10, 15))
    plt.subplot(4, 1, 1)
    plt.plot(data['seconds_elapsed'], data['acc_x'])
    plt.plot(data['seconds_elapsed'], data['acc_y'])
    plt.plot(data['seconds_elapsed'], data['acc_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Accelerometer')
    plt.grid(True)
    plt.subplot(4, 1, 2)
    plt.plot(data['seconds_elapsed'], data['gra_x'])
    plt.plot(data['seconds_elapsed'], data['gra_y'])
    plt.plot(data['seconds_elapsed'], data['gra_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Gravity')
    plt.grid(True)
    plt.subplot(4, 1, 3)
    plt.plot(data['seconds_elapsed'], data['gyr_x'])
    plt.plot(data['seconds_elapsed'], data['gyr_y'])
    plt.plot(data['seconds_elapsed'], data['gyr_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Gyroscope')
    plt.grid(True)
    plt.subplot(4, 1, 4)
    plt.plot(data['seconds_elapsed'], data['ori_x'])
    plt.plot(data['seconds_elapsed'], data['ori_y'])
    plt.plot(data['seconds_elapsed'], data['ori_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Orientation')
    plt.grid(True)
    plt.show()

def add_values_to_previous_list(previous_list, values):
    if not previous_list:
        # Handle the case when the previous_list is empty
        # You can set a default majority value or take any other appropriate action
        return
    majority_value = max(set(previous_list), key=previous_list.count)
    previous_list.extend([majority_value] * len(values))


def majority_value(lst):
    if not lst:
        return None
    return max(set(lst), key=lst.count)


def process_predictions(lst, min_length):
    res = []
    current_list = []

    for i in range(len(lst)):
        if i == 0 or lst[i] == lst[i - 1]:
            current_list.append(lst[i])
        else:
            res.append(current_list)
            current_list = [lst[i]]

    res.append(current_list)

    resul = []
    previous_list = []
    for sublist in res:
        if len(sublist) >= min_length:
            if previous_list:
                resul.append(previous_list)
                previous_list = []
            resul.append(sublist)
        else:
            add_values_to_previous_list(previous_list, sublist)

    # Add the last previous_list if it's not empty
    if previous_list:
        resul.append(previous_list)

    result = []
    current_list = []
    for sublist in resul:
        if not current_list:
            current_list = sublist
        elif majority_value(sublist) == majority_value(current_list):
            current_list.extend(sublist)
        else:
            result.append(current_list)
            current_list = sublist
    # Append the last list
    if current_list:
        result.append(current_list)

    return result


def recognize_exercise(file_path, scr=False):
    model = tf.keras.models.load_model('prediction/models/LSTM_w150_o75_e100_p33')
    print(file_path)
    test_file = pd.read_excel(file_path)
    window_size = 150
    overlap = 15
    windows_pred = sliding_windows(test_file, window_size, overlap)

    x = []
    activit = {
        0: 'NULL',
        1: 'BEND',
        2: 'CIRCULAR RAISE',
        3: 'ABDUCTION',
        4: 'REAR TOUCH',
        5: 'SIDE BEND'
    }
    if scr:
        labels = []
        for i in range(len(windows_pred)):
            label = windows_pred[i]['activity'].value_counts().idxmax()
            if windows_pred[i].values.shape[0] == window_size:
                labels.append(label)
        y = to_categorical(labels)

    for i in range(len(windows_pred)):
        windows_pred[i].drop('activity', axis='columns', inplace=True)
        windows_pred[i].drop('time', axis='columns', inplace=True)
        windows_pred[i].drop('seconds_elapsed', axis='columns', inplace=True)
        windows_pred[i].drop('Unnamed: 0', axis='columns', inplace=True)
        if windows_pred[i].values.shape[0] == window_size:
            x.append(windows_pred[i].values)

    X = np.array(x)

    act = []
    for i in range(len(X)):
        if scr:
            actual_label = np.nonzero(labels[i])[0]
        a = tf.expand_dims(X[i], axis=0)
        pred = model.predict(a)
        pred_label = np.argmax(pred, axis=1)
        act.append(pred_label[0])

    if scr:
        correct = 0
        for i in range(len(act)):
            if act[i] == labels[i]:
                correct += 1
        score = correct * 100 / len(act)
        print(f'Score: {score}%')

    processed_predictions = process_predictions(act, 8)

    act_final = []
    start = 0
    end = 0
    for i in processed_predictions:
        end += round(len(i) * 15 / 92.26, 2)
        sub_df = test_file[(test_file['seconds_elapsed'] >= start) & (test_file['seconds_elapsed'] < end)].copy()
        act_final.append({'activity_int': int(majority_value(i)), 'activity': activit[majority_value(i)], 'length': len(i),
                          'duration[s]': round(len(i) * 15 / 92.26, 2), 'start[s]': round(start, 2),
                          'end[s]': round(end, 2), 'sub_df': sub_df})
        start += round(len(i) * 15 / 92.26, 2)

    return act_final

def zero_crossings(signal):
    zero_crossings = np.where(np.diff(np.sign(signal)))[0]
    n = int(len(zero_crossings)/2)
    return n

def repetition_counter(frame, sensor='acc'):
    activity = frame['activity']
    data = frame['sub_df']
    sample = np.arange(len(data))
    time = data['seconds_elapsed'].to_numpy()
    x = data[f'{sensor}_x'].to_numpy()
    y = data[f'{sensor}_y'].to_numpy()
    z = data[f'{sensor}_z'].to_numpy()
    a_all = []
    for (xi, yi, zi) in zip(x,y,z):
        a = np.sqrt(xi**2 + yi**2 + zi**2)
        a_all.append(a)

    a_all = np.array(a_all)
    a_final = []

    for i in a_all:
        a = i - np.mean(a_all)
        a_final.append(a)

    a_final = np.array(a_final)

    fs = 3500  # Sampling frequency
    # Generate the time vector properly
    t = np.arange(len(time)) / fs
    zero = np.zeros(len(t))
    fc = 20  # Cut-off frequency of the filter
    w = fc / (fs / 2) # Normalize the frequency
    b, a = signal.butter(5, w, 'low')
    filtered = signal.filtfilt(b, a, a_final)

    peaks = signal.find_peaks(filtered)

    x_peaks = []
    for i in peaks[0]:
       x_peaks.append(t[i])

    y_peaks = []
    for i in range(len(filtered)):
        if i in peaks[0]:
            y_peaks.append(filtered[i])
    zeros = zero_crossings(filtered)

    # plt.figure(figsize=(15,15))
    # plt.subplot(3,1,1)
    # plt.plot(time, x)
    # plt.plot(time, y)
    # plt.plot(time, z)
    # plt.title('Acceleration values on X, Y, and Z-axis')
    # plt.xlabel('Time [s]')
    # plt.ylabel('Acceleration [m/s2]')
    # plt.legend(['x', 'y', 'z'])
    # # plt.xlim(0,np.max(time))
    # plt.grid(True)
    # plt.subplot(3,1,2)
    # plt.plot(time, a_final)
    # plt.title('Sum of Acceleration Vectors of X, Y, and Z-axis after subtracting the mean value')
    # plt.xlabel('Time [s]')
    # plt.ylabel('Acceleration [m/s2]')
    # # plt.xlim(0,np.max(time))
    # plt.grid(True)
    # plt.subplot(3,1,3)
    # plt.plot(t, filtered, color='red', label='filtered')
    # plt.plot(t, zero, '--', color='gray', label='zero')
    # plt.scatter(x_peaks, y_peaks, marker="o", s=150, facecolors='none', edgecolor='red', linewidths=3, label='peaks')
    # plt.title('Filtered signal')
    # # plt.xlim(np.min(t),np.max(t))
    # plt.legend()
    # plt.grid(True)
    # plt.show()
    repetition_count_peaks = len(x_peaks)
    repetition_count_zero_crossing = int(zeros)


    print(f'Detected activity is {activity}')
    print(f'There are {len(peaks[0])} peaks in the signal, which means that exercise is repeated {int(len(peaks[0]))} times.')
    print(f'Signal crosses zero {zeros*2} times, which means that exercise is repeated {int(zeros)} times.')

    return repetition_count_peaks, repetition_count_zero_crossing, time, x, y, z, a_final, t, filtered, zero, x_peaks, y_peaks


def reh_app(file_path, sc=False):
    print(file_path)
    recognized_df = recognize_exercise(file_path, sc)
    activities_final_counted = []
    for i in range(len(recognized_df)):
        if recognized_df[i]['activity_int'] != 0:
            repetition_count_peaks, repetition_count_zero_crossing, time, x, y, z, a_final, t, filtered, zero, x_peaks, y_peaks = repetition_counter(recognized_df[i])
            # activities_final_counted.append([recognized_df[i]['activity'], peaks, zeros])
            recognized_df[i]['repetition counts peaks'] = repetition_count_peaks
            recognized_df[i]['repetition counts zero crossing'] = repetition_count_zero_crossing
            recognized_df[i]['acc_time'] = time.tolist()
            recognized_df[i]['acc_x'] = x.tolist()
            recognized_df[i]['acc_y'] = y.tolist()
            recognized_df[i]['acc_z'] = zero.tolist()
            recognized_df[i]['combined axis acc'] = a_final.tolist()
            recognized_df[i]['time fr domain'] = repetition_count_peaks
            recognized_df[i]['filtered acc'] = t.tolist()
            recognized_df[i]['zero line'] = zero.tolist()
            recognized_df[i]['x_peaks'] = x_peaks
            recognized_df[i]['y_peaks'] = y_peaks
    # print(recognized_df)

    BEND = 0
    CIRCULAR_RISE = 0
    ABDUCTION = 0
    REAR_TOUCH = 0
    SIDE_BEND = 0

    for i in range(len(recognized_df)):
        if recognized_df[i]['activity_int'] == 1:
            BEND += recognized_df[i]['repetition counts peaks']
        elif recognized_df[i]['activity_int'] == 2:
            CIRCULAR_RISE += recognized_df[i]['repetition counts peaks']
        elif recognized_df[i]['activity_int'] == 3:
            ABDUCTION += recognized_df[i]['repetition counts peaks']
        elif recognized_df[i]['activity_int'] == 4:
            REAR_TOUCH += recognized_df[i]['repetition counts peaks']
        elif recognized_df[i]['activity_int'] == 5:
            SIDE_BEND += recognized_df[i]['repetition counts peaks']

    summary_count = {
        'BEND': BEND,
        'CIRCULAR_RISE': CIRCULAR_RISE,
        'ABDUCTION': ABDUCTION,
        'REAR_TOUCH': REAR_TOUCH,
        'SIDE_BEND': SIDE_BEND
    }

    duration = recognized_df[-1]['end[s]']

    return recognized_df, summary_count, duration



# df = reh_app('C:/Users/jakub/PycharmProjects/RehApp/backend/data/test/ala_2.xlsx', True)