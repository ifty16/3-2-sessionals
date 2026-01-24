import pandas as pd
import numpy as np

np.random.seed(42)

# 1. Mean Imputation
def mean_imputation(x):
    # TODO: Mean imputation (column-wise)
    
    return x_imputed # of shape as x

# 2. Leaky ReLU
def leaky_relu(x, alpha=0.01):
    # TODO: Leaky ReLU function
    
    return value # of shape as x

# 3. Leaky ReLU gradient
def leaky_relu_gradient(x, dout=1, alpha=0.01):
    # TODO: Leaky ReLU gradient
    
    return grad # of shape as x

# 4. Huber loss
def huber_loss(y_pred, y_true, delta=1.0):
    # TODO: Huber loss
    
    return loss # only a scalar value

# 5. Huber loss gradient
def huber_loss_gradient(y_pred, y_true, delta=1.0):
    # TODO: Huber loss gradient
    
    return grad # of shape as y_pred

# 6. Inference on test data and evaluate RMSE
def inference(df_test, W, b, X_train):
    # TODO: Load test data, apply same preprocessing, and evaluate RMSE.

    return test_rmse

def rmse_loss(y_pred, y_true):
    n = len(y_pred)
    mse = (1/n) * np.sum((y_pred - y_true) ** 2)
    return np.sqrt(mse)

# ============================
# MAIN: MINIBATCH TRAINING + RMSE
# ============================
if __name__ == "__main__":
    df = pd.read_csv("train_data.csv", header=None)
    print("Data size:", df.shape)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values.reshape(-1, 1)

    print("NaN values in X before imputation:", np.isnan(X).sum())
    print("Performing mean imputation for missing values...")
    X = mean_imputation(X)
    print("NaN values in X after imputation:", np.isnan(X).sum())
    n_samples, n_features = X.shape

    # Initialize parameters
    W = np.zeros((n_features, 1))
    b = 0.0

    batch_size = 64
    learning_rate = 0.05
    num_epochs = 15

    print(f"\nTraining for {num_epochs} epochs with learning rate {learning_rate}...\n")

    # Training loop
    for epoch in range(num_epochs):
        epoch_loss = 0.0
        num_batches = 0

        # Shuffle data at the beginning of each epoch
        indices = np.random.permutation(n_samples)
        X_shuffled = X[indices]
        y_shuffled = y[indices]

        for i in range(0, n_samples, batch_size):
            Xb = X_shuffled[i:i+batch_size]
            yb = y_shuffled[i:i+batch_size]

            outputs = Xb @ W + b
            preds = leaky_relu(outputs)

            # Compute loss
            batch_loss = huber_loss(preds, yb)
            epoch_loss += batch_loss
            num_batches += 1

            # Gradient of loss w.r.t predictions
            dloss_dpreds = huber_loss_gradient(preds, yb)

            # Gradient of Leaky ReLU
            dpreds_doutputs = leaky_relu_gradient(outputs, dout=dloss_dpreds)

            # Gradients w.r.t W and b
            dW = Xb.T @ dpreds_doutputs
            db = np.sum(dpreds_doutputs)

            # Update weights
            W -= learning_rate * dW
            b -= learning_rate * db

        avg_loss = epoch_loss / num_batches

        # Calculate RMSE on full dataset
        outputs_all = X @ W + b
        y_pred = leaky_relu(outputs_all)
        rmse = rmse_loss(y_pred, y)

        print(f"Epoch {epoch+1}/{num_epochs} - Loss: {avg_loss:.6f}, RMSE: {rmse:.4f}")

    print("\n" + "="*50)
    print("Training completed!")
    print("="*50)

    # Final evaluation
    outputs_final = X @ W + b
    preds_final = leaky_relu(outputs_final)
    final_loss = huber_loss(preds_final, y)
    rmse_final = rmse_loss(preds_final, y)

    print(f"\nFinal Huber Loss: {final_loss:.6f}")
    print(f"Final RMSE: {rmse_final:.4f}")
    print("\nTrained weights (W):", W.ravel())
    print(f"Trained bias (b): {b:.6f}")

    # ============================
    # INFERENCE ON TEST DATA
    # ============================

    df_test = pd.read_csv("test_data.csv", header=None)

    test_rmse = inference(df_test, W, b, X)

    print(f"Test RMSE: {test_rmse:.6f}")