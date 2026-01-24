import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

if __name__ == "__main__":
    # --- 1. Data Loading (Same as before) ---
    df = pd.read_csv("Section-A/files/mnist1.csv")
    X_numpy = df.iloc[:, :-1].values
    y_numpy = df.iloc[:, -1].values

    # --- 2. Data Preprocessing (CRITICAL CHANGE) ---
    # PyTorch needs Tensors, not Numpy arrays.
    # Note: We do NOT one-hot encode y. PyTorch CrossEntropyLoss wants class indices (0-9).
    X_tensor = torch.tensor(X_numpy, dtype=torch.float32)
    y_tensor = torch.tensor(y_numpy, dtype=torch.long) # Must be Long (integers)

    # Create a DataLoader (This handles batching automatically)
    dataset = TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # --- 3. Define the Model ---
    # nn.Sequential is the direct equivalent of tf.keras.Sequential
    model = nn.Sequential(
        nn.Linear(X_numpy.shape[1], 64), # Input -> Hidden 1
        nn.ReLU(),
        nn.Linear(64, 32),               # Hidden 1 -> Hidden 2
        nn.ReLU(),
        nn.Linear(32, 10)                # Hidden 2 -> Output (Logits)
    )

    # --- 4. Loss & Optimizer ---
    criterion = nn.CrossEntropyLoss() # Combines Softmax + Categorical Cross Entropy
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # --- 5. The Training Loop (Look familiar?) ---
    epochs = 100
    for epoch in range(epochs):
        epoch_loss = 0.0
        correct = 0
        total = 0

        for batch_X, batch_y in dataloader:
            # A. Forward Pass
            predictions = model(batch_X)
            loss = criterion(predictions, batch_y)

            # B. Backward Pass (The "Magic" Step)
            optimizer.zero_grad() # Reset gradients to 0 (unlike numpy, they accumulate)
            loss.backward()       # Calculate dW, db automatically
            optimizer.step()      # Update weights: W = W - lr * dW

            # Tracking metrics
            epoch_loss += loss.item()
            _, predicted_class = torch.max(predictions, 1)
            correct += (predicted_class == batch_y).sum().item()
            total += batch_y.size(0)

        # Print metrics every 10 epochs
        if (epoch + 1) % 10 == 0:
            acc = correct / total
            print(f"Epoch {epoch+1}: Loss {epoch_loss/len(dataloader):.4f} | Accuracy: {acc:.4f}")

    # --- 6. Evaluation ---
    model.eval() # Switch to evaluation mode
    with torch.no_grad(): # Disable gradient calculation (saves RAM)
        outputs = model(X_tensor)
        _, predicted = torch.max(outputs, 1)
        accuracy = (predicted == y_tensor).sum().item() / y_tensor.size(0)
        print(f"\nFinal Accuracy: {accuracy:.4f}")
