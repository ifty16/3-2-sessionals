import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from torch.optim.optimizer import Optimizer


# ==========================================
# PART 1: DEFINE THE CNN (Modeling)
# ==========================================
class MockCNN(nn.Module):
    def __init__(self):
        super(MockCNN, self).__init__()

        # TODO 1: Define Conv Layer
        # Input: (Batch, 1, 32, 32)
        # Requirements: 32 filters, 3x3 kernel, stride 1, padding 1
        self.conv1 = nn.Conv2d(
            in_channels=1,
            out_channels=32,
            kernel_size=3,
            stride=1,
            padding=1,
        )

        self.relu = nn.ReLU()

        # TODO 2: Define Pooling
        # Requirement: MaxPool that cuts dimensions by half (2x2)
        self.pool = nn.MaxPool2d(kernel_size=2)

        # TODO 3: Calculate Linear Input Size (The Math Part!)
        # Step A: Input starts at 32x32.
        # Step B: After Conv (pad=1, stride=1), size is 32?
        # Step C: After Pool (2x2), size is 16?
        # Step D: Total features = Channels * Height * Width
        self.flatten_size = 32 * 16 * 16

        self.fc = nn.Linear(self.flatten_size, 10)

    def forward(self, x):
        # Data flow: Conv -> ReLU -> Pool -> Flatten -> Linear
        x = self.pool(self.relu(self.conv1(x)))

        # TODO 4: Flatten the tensor
        # We need shape (Batch, flatten_size)
        x = x.view(x.size(0), -1)

        x = self.fc(x)
        return x


# ==========================================
# PART 2: OPTIMIZATION & LOOP (Code Completion)
# ==========================================
def train_one_epoch(model, loader):
    # TODO 5: Define Optimizer (Adam, lr=0.001)
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Define Loss (Cross Entropy for classification)
    criterion = nn.CrossEntropyLoss()

    model.train()  # Set mode

    for images, labels in loader:
        # TODO 6: The "5 Magic Lines" of Training

        # A. Reset Gradients
        optimizer.zero_grad()

        # B. Forward Pass
        outputs = model(images)

        # C. Calculate Loss
        loss = criterion(outputs, labels)

        # D. Backward Pass (Gradients)
        loss.backward()

        # E. Update Weights
        optimizer.step()

    print("Epoch complete")


# -------------------------------------------------
# SELF-CHECK (Mental Walkthrough)
# -------------------------------------------------
# If input is 32x32...
# Conv (pad 1) -> 32x32
# Pool (2x2)   -> 16x16
# Channels     -> 32
# Flatten Size -> 32 * 16 * 16 = 8192

if __name__ == "__main__":
    # Set random seeds for reproducibility
    torch.manual_seed(0)
    np.random.seed(0)
    random.seed(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Data Preparation
    transform = transforms.Compose(
        [
            transforms.Resize((32, 32)),
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,)),
        ]
    )

    train_dataset = datasets.MNIST(
        root="./data",
        train=True,
        download=False,
        transform=transform,
    )

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # Model Initialization
    model = MockCNN().to(device)

    # Training Loop
    num_epochs = 5
    for epoch in range(num_epochs):
        print(f"Epoch {epoch + 1}/{num_epochs}")
        train_one_epoch(model, train_loader)

        # Evaluate accuracy
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in train_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total
        print(f"Accuracy: {accuracy:.2f}%")
