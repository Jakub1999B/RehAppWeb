from keras.utils import to_categorical
from sklearn.model_selection import train_test_split
import numpy as np
import os
import pandas as pd


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


def load_dataset(dir_path, window_size, overlap):
    file_list = os.listdir(dir_path)
    files = []
    windows_all = []
    x = []

    for i in file_list:
        if dir_path[-1] == 'n':
            data = pd.read_csv(f'{dir_path}/{i}')
        elif dir_path[-1] == 't':
            data = pd.read_excel(f'{dir_path}/{i}')
        files.append(data)
        windows = sliding_windows(data, window_size, overlap)
        for window in windows:
            windows_all.append(window)

    labels = []
    for i in range(len(windows_all)):
        label = windows_all[i]['activity'].value_counts()[:1].index.to_list()
        if windows_all[i].values.shape[0] == window_size:
            labels.append(label[0])
    y = to_categorical(labels)

    for i in range(len(windows_all)):
        windows_all[i].drop('activity', axis='columns', inplace=True)
        windows_all[i].drop('time', axis='columns', inplace=True)
        windows_all[i].drop('seconds_elapsed', axis='columns', inplace=True)
        if 'Unnamed: 0' in windows_all[i].columns:
            windows_all[i].drop('Unnamed: 0', axis='columns', inplace=True)
        if windows_all[i].values.shape[0] == window_size:
            x.append(windows_all[i].values)

    X = np.array(x)
    return X, y


def load_train_test_val(dir_path_train, dir_path_test, window_size, overlap, val_split):
    # upload train and test dataset
    trainX, trainy = load_dataset(dir_path_train, window_size, overlap)
    testX, testy = load_dataset(dir_path_test, window_size, overlap)

    # splot train dataset into train and val
    trainX, valX, trainy, valy = train_test_split(trainX, trainy, test_size=val_split, random_state=42)

    return trainX, trainy, testX, testy, valX, valy


def load_to_predict(file_path, window_size, overlap):
    data = pd.read_excel(file_path)
    windows = sliding_windows(data, window_size, overlap)
    for window in windows:
        windows_all.append(window)

    labels = []
    for i in range(len(windows_all)):
        label = windows_all[i]['activity'].value_counts()[:1].index.to_list()
        if windows_all[i].values.shape[0] == window_size:
            labels.append(label[0])
    y = to_categorical(labels)

    for i in range(len(windows_all)):
        windows_all[i].drop('activity', axis='columns', inplace=True)
        windows_all[i].drop('time', axis='columns', inplace=True)
        windows_all[i].drop('seconds_elapsed', axis='columns', inplace=True)
        if 'Unnamed: 0' in windows_all[i].columns:
            windows_all[i].drop('Unnamed: 0', axis='columns', inplace=True)
        if windows_all[i].values.shape[0] == window_size:
            x.append(windows_all[i].values)

    X = np.array(x)

    return X, y
