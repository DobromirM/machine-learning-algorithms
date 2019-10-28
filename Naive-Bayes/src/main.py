import pandas as pd
from utils import label_data_split, split_train_test
from naive_bayes import NaiveBayes

if __name__ == "__main__":
    data = pd.read_csv('resources/data.csv')
    x, y = label_data_split(data, 'class')

    x_train, y_train, x_test, y_test = split_train_test(x, y, 0.7)

    model = NaiveBayes(x_train, y_train)
    model.fit()

    predictions = model.predict(x_test)

    accuracy = (predictions == y_test).sum() / len(predictions) * 100
    print(f'Accuracy: {accuracy}%')
