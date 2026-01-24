import numpy as np
import pandas as pd
import tensorflow as tf

if __name__ == "__main__":
    df = pd.read_csv("files/mnist1.csv")
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values.reshape(-1, 1)

    num_classes = 10
    y_encoded = np.zeros((y.shape[0], num_classes))
    row_i = np.arange(y.shape[0])
    class_i = y.flatten().astype(int)
    y_encoded[row_i, class_i] = 1
    y = y_encoded

    model = tf.keras.Sequential(
        [
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(10, activation="softmax"),
        ]
    )
    model.compile(
        optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"]
    )
    history = model.fit(X, y, epochs=100)

    loss, accuracy = model.evaluate(X, y, verbose=0)
    print(f"Accuracy: {accuracy:.4f}")
