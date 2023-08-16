import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
import keras
import pandas as pd
from keras.utils import to_categorical


def sliding_windows_0(data, window_size, overlap):
    ind = 0
    windows = []
    for i in range(len(data)- window_size + 1):
        end = ind + window_size
        window = data[ind:end]
        windows.append(window)
        ind += window_size
        if ind > len(data):
            break
    return windows


def plot_data(data):
    data = pd.read_excel(data)
    plt.figure(figsize=(10,15))
    plt.subplot(4,1,1)
    plt.plot(data['seconds_elapsed'], data['acc_x'])
    plt.plot(data['seconds_elapsed'], data['acc_y'])
    plt.plot(data['seconds_elapsed'], data['acc_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Accelerometer')
    plt.grid(True)
    plt.subplot(4,1,2)
    plt.plot(data['seconds_elapsed'], data['gra_x'])
    plt.plot(data['seconds_elapsed'], data['gra_y'])
    plt.plot(data['seconds_elapsed'], data['gra_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Gravity')
    plt.grid(True)
    plt.subplot(4,1,3)
    plt.plot(data['seconds_elapsed'], data['gyr_x'])
    plt.plot(data['seconds_elapsed'], data['gyr_y'])
    plt.plot(data['seconds_elapsed'], data['gyr_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Gyroscope')
    plt.grid(True)
    plt.subplot(4,1,4)
    plt.plot(data['seconds_elapsed'], data['ori_x'])
    plt.plot(data['seconds_elapsed'], data['ori_y'])
    plt.plot(data['seconds_elapsed'], data['ori_z'])
    plt.legend(['x', 'y', 'z'])
    plt.title('Orientation')
    plt.grid(True)

    plt.show()


def analyze_file(file, window_size, overlap, model, score):
    windows_pred = sliding_windows_0(file, window_size, overlap)

    x = []
    activit = {
      0:'NULL',
      1:'BEND',
      2:'CIRCULAR RAISE',
      3:'ABDUCTION',
      4:'REAR TOUCH',
      5:'SIDE BEND'
    }

    if score:
        labels = []
        for i in range(len(windows_pred)):
            label = windows_pred[i]['activity'].value_counts()[:1].index.to_list()
            if windows_pred[i].values.shape[0] == window_size:
                labels.append(label[0])
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
        if score:
            actual_label = np.nonzero(labels[i])[0]
        a = tf.expand_dims(X[i], axis=0)
        pred = model.predict(a)
        pred_label = np.argmax(pred, axis=1)
        act.append(activit[pred_label[0]])

    if score:
        correct = 0
        for i in range(len(act)):
            if act[i] == activit[labels[i]]:
                correct += 1
        score = correct*100/len(act)
        print(f'Score: {score}%')

    end_times = []
    activities = []
    for i in range(1, len(act)):
        if act[i] != act[i-1]:
            end_times.append(i*window_size/100)
            activities.append(act[i-1])
        if i == len(act)-1:
            end_times.append((i+1)*window_size/100)
            activities.append(act[i])

    durations = []
    for i in range(len(end_times)):
        if i == 0:
            durations.append(end_times[i])
        else:
            time = end_times[i] - end_times[i-1]
            durations.append(time)

    for i in range(len(activities)):
        print(f'ACTIVITY: {activities[i]},  END TIME: {round(end_times[i], 2)},   DURATION: {round(durations[i], 2)}')

    print(f'TOTAL TRAINING TIME: {end_times[len(activities)-1]}')

    plot_data_0(file)

    return act, activities, end_times, durations
