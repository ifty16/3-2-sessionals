import pandas as pd
import numpy as np


def load_and_fill_nulls(filename, fill_value=0):
    df = pd.read_csv(filename)

    print("Dataset loaded successfully!")
    print("Shape:", df.shape)
    print("\nFirst few rows:")
    print(df.head())

    print("\nNull values per column before filling:")
    print(df.isnull().sum())

    df = df.fillna(fill_value)

    print("\nNull values per column after filling:")
    print(df.isnull().sum())

    return df


# ============================
# MAIN: LOGISTIC REGRESSION
# ============================
if __name__ == "__main__":

    # Load data
    df = load_and_fill_nulls("Iris.csv", fill_value=0)

    # ---------------------------------
    # Convert STRING labels to BINARY
    # 1 = Iris-setosa, 0 = others
    # ---------------------------------
    df.iloc[:, -1] = (df.iloc[:, -1] == "Iris-setosa").astype(int)

    # Separate features and labels
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values.reshape(-1, 1).astype(np.float64)

    # Normalize features
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    n_samples, n_features = X.shape

    # Initialize parameters
    W = np.zeros((n_features, 1))
    b = 0.0

    # Hyperparameters
    learning_rate = 0.1
    epochs = 100
    batch_size = 32

    # Sigmoid function
    def sigmoid(z):
        return 1 / (1 + np.exp(-z))

    print("\nTraining Logistic Regression using Gradient Descent...\n")

    # ============================
    # TRAINING LOOP
    # ============================
    for epoch in range(epochs):

        for i in range(0, n_samples, batch_size):
            Xb = X[i:i + batch_size]
            yb = y[i:i + batch_size]

            # Forward pass
            z = Xb @ W + b
            y_hat = sigmoid(z)

            # Binary Cross Entropy Loss
            loss = -np.mean(
                yb * np.log(y_hat + 1e-8) +
                (1 - yb) * np.log(1 - y_hat + 1e-8)
            )

            # Gradients
            dW = (1 / len(Xb)) * Xb.T @ (y_hat - yb)
            db = (1 / len(Xb)) * np.sum(y_hat - yb)

            # Update
            W = W - learning_rate * dW
            b = b - learning_rate * db

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.4f}")

    # ============================
    # INFERENCE & ACCURACY
    # ============================
    z = X @ W + b
    y_hat = sigmoid(z)
    y_pred = (y_hat >= 0.5).astype(int)

    accuracy = np.mean(y_pred == y)

    print("\nTraining completed.")
    print("Final Accuracy:", accuracy)
    print("Final Weights:", W.ravel())
    print("Final Bias:", b)
