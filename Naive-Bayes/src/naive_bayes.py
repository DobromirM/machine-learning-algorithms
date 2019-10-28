import pandas as pd
import numpy as np


class NaiveBayes:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.summary = dict()
        self.count_per_class = dict()
        self.predictions = pd.Series()

    def fit(self):
        self.build_summary()

    def predict(self, data):
        for index, row in data.iterrows():

            preds = dict()

            for clasz, value in self.summary.items():

                class_pred = 1

                for attribute in value.index:
                    stats = self.summary[clasz].loc[attribute]
                    class_pred = class_pred * self.calculate_probability(row.loc[attribute], stats['mean'], stats['std'])

                preds[clasz] = class_pred * self.count_per_class[clasz] / len(self.x)

            self.predictions.at[index] = max(preds, key=preds.get)

        return self.predictions

    def build_summary(self):
        separated_data = self.separate_by_class()

        for clasz, value in separated_data.items():
            stats = {'mean': value.mean(), 'std': value.std()}
            self.summary[clasz] = pd.DataFrame(stats)
            self.count_per_class[clasz] = len(value)

    def separate_by_class(self):
        classes = self.y.unique()

        separated_data = dict()

        for clasz in classes:
            separated_data[clasz] = self.x.loc[self.y == clasz]

        return separated_data

    def calculate_probability(self, x, mean, std):

        variance = std ** 2
        return 1 / np.sqrt(2 * np.pi * variance) * np.exp(-(x - mean) ** 2 / (2 * variance))
