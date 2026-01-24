import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

if __name__ == "__main__":
    df = pd.read_csv('Section-A/files/mnist1.csv')
    X = df.iloc[:, :-1].values
    y = df.iloc[:, -1].values

    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.long)

    dataset = TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=128, shuffle=True)

    model = nn.Sequential(
        nn.Linear(X.shape[1], 64),
        nn.ReLU(),
        nn.Linear(64, 32),
        nn.ReLU(),
        nn.Linear(32, 10)
    )

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 1000
    for epoch in range(epochs):
        epoch_loss = 0
        correct = 0
        total = 0

        for X_batch, y_batch in dataloader:
            predictions = model(X_batch)
            loss = criterion(predictions, y_batch)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            _, predicted_class = torch.max(predictions, 1)
            correct += (predicted_class == y_batch).sum().item()
            total += y_batch.size(0)

        if (epoch + 1) % 10 == 0:
            acc = correct / total
            print(
                f"Epoch {epoch+1}: Loss {epoch_loss/len(dataloader):.4f} | Accuracy: {acc:.4f}"
            )

    model.eval()
    with torch.no_grad():
        outputs = model(X_tensor)
        _, predicted = torch.max(predictions, 1)
        accuracy = (predicted == y_tensor).sum().item() / y_tensor.size(0)
        print(f"\nFinal Accuracy: {accuracy:.4f}")
