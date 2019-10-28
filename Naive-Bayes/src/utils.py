import pandas as pd
import numpy as np


def label_data_split(data, label):
    if isinstance(label, str):
        name = label
        x = data.loc[:, data.columns != name]
        y = data[name]

    elif isinstance(label, int):
        index = label
        x = data.iloc[:, index + 1:]
        y = data.iloc[:, index]

    else:
        raise Exception("The label must be either a string or an integer!")

    return x, y


def split_train_test(x, y, train_ratio, seed=None):
    count = len(x)
    train_count = round(count * train_ratio)

    selection_range = range(0, count)

    np.random.seed(seed)
    train_index = np.random.choice(selection_range, train_count, replace=False)
    mask = np.isin(selection_range, train_index)

    x_train = x[mask]
    x_test = x[~mask]
    y_train = y[mask]
    y_test = y[~mask]

    return x_train, y_train, x_test, y_test
