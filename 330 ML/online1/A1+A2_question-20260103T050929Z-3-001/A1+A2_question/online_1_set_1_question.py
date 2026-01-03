import pandas as pd
import numpy as np
np.random.seed(42)

# 1. Standardization (Z-score)
def standardization(x):
    # TODO: Standardization
    mean = np.mean(x, axis=0) #axis=0 means column-wise
    std = np.std(x, axis=0) + 1e-8 # to avoid division by zero
    X_scaled = (x - mean) / std
    return X_scaled # of shape as x

# 2. Sigmoid
def sigmoid(x):
    # TODO: Sigmoid function
    value = 1/(1+np.exp(-x))
    return value # of shape as x

# 3. Sigmoid gradient
def sigmoid_gradient(x, dout=1):
    # TODO: Sigmoid gradient
    s= sigmoid(x)
    grad = dout * s * (1 - s)
    return grad # of shape as x

# 4. MSE Loss
def mse_loss(y_pred, y_true):
    # TODO: MSE loss
    
    loss = np.mean((y_pred - y_true) ** 2)
    return loss # only a scalar value

# 5. MSE Loss gradient
def mse_loss_gradient(y_pred, y_true):
    # TODO: MSE loss gradient
    grad = (2 / y_true.shape[0]) * (y_pred - y_true)
    return grad # of shape as y_pred

# ============================
# MAIN: MINIBATCH TRAINING + ACCURACY
# ============================
if __name__ == "__main__":
    df = pd.read_csv("train_data.csv", header=None)
    df = df.fillna(-1.513682)
    print("Data size:", df.shape)

    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values.reshape(-1, 1)

    # Normalize
    X = standardization(X)

    n_samples, n_features = X.shape

    # Initialize parameters
    W = np.zeros((n_features, 1))
    b = 0.0

    batch_size = 50
    learning_rate = 0.1
    num_epochs = 10

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
            
            logits = Xb @ W + b
            preds = sigmoid(logits)
            
            # Compute loss
            batch_loss = mse_loss(preds, yb)
            epoch_loss += batch_loss
            num_batches += 1
            
            # Gradient of loss w.r.t predictions
            dloss_dpreds = mse_loss_gradient(preds, yb)
            
            # Gradient of sigmoid
            dpreds_dlogits = sigmoid_gradient(logits, dout=dloss_dpreds)
            
            # Gradients w.r.t W and b
            dW = Xb.T @ dpreds_dlogits
            db = np.sum(dpreds_dlogits)
            
            # Update weights
            W -= learning_rate * dW
            b -= learning_rate * db
        
        avg_loss = epoch_loss / num_batches
        
        # Calculate accuracy on full dataset
        logits_all = X @ W + b
        preds_all = sigmoid(logits_all)
        y_pred_class = (preds_all >= 0.5).astype(int)
        accuracy = np.mean(y_pred_class == y)
        
        print(f"Epoch {epoch+1}/{num_epochs} - Loss: {avg_loss:.6f}, Accuracy: {accuracy:.4f}")

    print("\n" + "="*50)
    print("Training completed!")
    print("="*50)

    # Final evaluation
    logits_final = X @ W + b
    preds_final = sigmoid(logits_final)
    final_loss = mse_loss(preds_final, y)
    
    y_pred_class_final = (preds_final >= 0.5).astype(int)
    final_accuracy = np.mean(y_pred_class_final == y)

    print(f"\nFinal MSE Loss: {final_loss:.6f}")
    print(f"Final Accuracy: {final_accuracy:.4f}")
    print("\nTrained weights (W):", W.ravel())
    print(f"Trained bias (b): {b:.6f}")