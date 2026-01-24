import pandas as pd
import numpy as np

np.random.seed(42)

# 1. Windowing Average Imputation
def windowing_average_imputation(x, k=3):
    """
    Fill missing values using average of k neighboring values.
    For each NaN, use average of k values before and k values after.
    LOOPS ARE ALLOWED for this function!
    """
    # TODO: Windowing average imputation
    x_imputed = x.copy()
    
    n_samples, n_features = x.shape
    
    # For each feature (column)
    for col in range(n_features):
        # Find NaN positions in this column
        nan_indices = np.where(np.isnan(x_imputed[:, col]))[0]
        
        # For each NaN position
        for idx in nan_indices:
            # Get window boundaries
            start = max(0, idx - k)
            end = min(n_samples, idx + k + 1)
            
            # Get values in window (excluding current position)
            window_values = []
            for i in range(start, end):
                if i != idx and not np.isnan(x_imputed[i, col]):
                    window_values.append(x_imputed[i, col])
            
            # If we have values, take mean; otherwise leave as NaN
            if len(window_values) > 0:
                x_imputed[idx, col] = np.mean(window_values)
    
    return x_imputed #of shape as x

# 2. Tanh
def tanh(x):
    """
    Hyperbolic tangent function
    Formula: tanh(x) = (e^x - e^(-x)) / (e^x + e^(-x))
    Or simply: np.tanh(x)
    """
    # TODO: Tanh function
    value = np.tanh(x)
    #value = (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))
    # Alternative: value = (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))
    
    return value # of shape as x

# 3. Tanh gradient
def tanh_gradient(x, dout=1):
    """
    Gradient of tanh function
    Formula: tanh'(x) = 1 - tanh(x)^2
    Then multiply by dout for chain rule
    """
    # TODO: Tanh gradient
    t = tanh(x)
    grad = (1 - t**2) * dout
    
    return grad # of shape as x

# 4. MAE
def mae(y_pred, y_true):
    """
    Mean Absolute Error
    Formula: MAE = mean(|y_pred - y_true|)
    """
    # TODO: MAE loss
    loss = np.mean(np.abs(y_pred - y_true))
    
    return loss # only a scalar value

# 5. MAE gradient
def mae_gradient(y_pred, y_true):
    """
    Gradient of MAE with respect to predictions
    Formula: sign(y_pred - y_true) / n
    """
    # TODO: MAE gradient
    n = y_pred.shape[0]
    grad = np.sign(y_pred - y_true) / n
    
    return grad # of shape as y_pred

# 6. Inference on test data and evaluate MAE
def inference(df_test, W, b, X):
    """
    Load test data, impute missing values, make predictions, calculate MAE.
    """
    # TODO: Load test data and evaluate MAE.
    
    # Extract features and target from test data
    X_test = df_test.iloc[:, :-1].values
    y_test = df_test.iloc[:, -1].values.reshape(-1, 1)
    
    # Impute missing values in test data using same method
    X_test = windowing_average_imputation(X_test, k=10)
    
    # Make predictions using trained weights
    outputs_test = X_test @ W + b
    y_pred_test = tanh(outputs_test)
    
    # Calculate MAE on test data
    test_mae = mae(y_pred_test, y_test)
    
    return test_mae

def mse_loss(y_pred, y_true):
    n = len(y_pred)
    loss = (1/n) * np.sum((y_pred - y_true) ** 2)
    return loss

# ============================
# MAIN: MINIBATCH TRAINING + ACCURACY
# ============================
if __name__ == "__main__":
    df = pd.read_csv("train_data.csv", header=None)
    print("Data size:", df.shape)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values.reshape(-1, 1)

    print("NaN values in X before imputation:", np.isnan(X).sum())
    print("Performing windowing average imputation for missing values...")
    X = windowing_average_imputation(X, k=10)
    print("NaN values in X after imputation:", np.isnan(X).sum())

    n_samples, n_features = X.shape

    # Initialize parameters
    W = np.zeros((n_features, 1))
    b = 0.0

    batch_size = 50
    learning_rate = 0.01
    num_epochs = 20

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
            preds = tanh(outputs)
            
            # Compute loss
            batch_loss = mae(preds, yb)
            epoch_loss += batch_loss
            num_batches += 1
            
            # Gradient of loss w.r.t predictions
            dloss_dpreds = mae_gradient(preds, yb)
            
            # Gradient of tanh
            dpreds_doutputs = tanh_gradient(outputs, dout=dloss_dpreds)
            
            # Gradients w.r.t W and b
            dW = Xb.T @ dpreds_doutputs
            db = np.sum(dpreds_doutputs)
            
            # Update weights
            W -= learning_rate * dW
            b -= learning_rate * db
        
        avg_loss = epoch_loss / num_batches
        
        # Calculate accuracy on full dataset
        outputs_all = X @ W + b
        y_pred = tanh(outputs_all)

        mse = mse_loss(y_pred, y)
        
        print(f"Epoch {epoch+1}/{num_epochs} - Loss: {avg_loss:.6f}, MSE: {mse:.4f}")

    print("\n" + "="*50)
    print("Training completed!")
    print("="*50)

    # Final evaluation
    outputs_final = X @ W + b
    preds_final = tanh(outputs_final)
    final_loss = mae(preds_final, y)
    mse_final = mse_loss(preds_final, y)

    print(f"\nFinal MAE Loss: {final_loss:.6f}")
    print(f"Final MSE: {mse_final:.4f}")
    print("\nTrained weights (W):", W.ravel())
    print(f"Trained bias (b): {b:.6f}")

    # ============================
    # INFERENCE ON TEST DATA
    # ============================

    df_test = pd.read_csv("test_data.csv", header=None)

    test_mae = inference(df_test, W, b, X)
    
    print(f"Test MAE: {test_mae:.6f}")