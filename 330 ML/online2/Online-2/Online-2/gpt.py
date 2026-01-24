# =============================
# IMPORTS (COMMON EXAM SET)
# =============================
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import numpy as np
import random


# =============================
# REPRODUCIBILITY
# =============================
def set_seed(seed=42):
    random.seed(seed)              # Python randomness
    np.random.seed(seed)           # NumPy randomness
    torch.manual_seed(seed)        # PyTorch CPU
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)  # PyTorch GPU

set_seed(42)


# =============================
# DEVICE (CPU / GPU)
# =============================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Alternative (exam):
# device = torch.device("cuda:0")


# =============================
# MODEL DEFINITION
# =============================
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()

        # -------- CONVOLUTION LAYERS --------
        self.conv1 = nn.Conv2d(
            in_channels=1,       # 1 for grayscale, 3 for RGB
            out_channels=16,     # number of filters
            kernel_size=3,       # filter size (3x3)
            stride=1,            # step size
            padding=1            # keeps spatial size same
        )

        # Alternative conv examples (exam):
        # nn.Conv2d(3, 32, kernel_size=5)
        # nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding)

        # -------- ACTIVATION FUNCTIONS --------
        self.relu = nn.ReLU()         # most common
        # self.sigmoid = nn.Sigmoid() # binary classification
        # self.tanh = nn.Tanh()       # outputs between -1 and 1
        # self.leaky_relu = nn.LeakyReLU(0.01)

        # -------- POOLING --------
        # self.pool = nn.MaxPool2d(2, 2)    # downsampling
        # self.pool = nn.AvgPool2d(2)

        # -------- NORMALIZATION --------
        # self.bn = nn.BatchNorm2d(16)      # batch normalization

        # -------- REGULARIZATION --------
        # self.dropout = nn.Dropout(p=0.5)  # prevent overfitting

        # -------- GLOBAL AVERAGE POOLING --------
        self.gap = nn.AdaptiveAvgPool2d((1, 1))

        # -------- FULLY CONNECTED LAYER --------
        self.fc = nn.Linear(16, 10)   # 10 classes (digits 0–9)
        # Alternative:
        # self.fc = nn.Linear(128, num_classes)


    def forward(self, x):
        # ----- CONVOLUTION -----
        x = self.conv1(x)

        # Optional additions (exam variants):
        # x = self.bn(x)

        # ----- ACTIVATION -----
        x = self.relu(x)
        # x = self.sigmoid(x)
        # x = self.tanh(x)

        # ----- POOLING -----
        # x = self.pool(x)

        # ----- DROPOUT -----
        # x = self.dropout(x)

        # ----- GAP -----
        x = self.gap(x)

        # ----- FLATTEN -----
        x = x.view(x.size(0), -1)
        # Alternative:
        # x = torch.flatten(x, 1)
        # x = nn.Flatten()(x)

        # ----- CLASSIFIER -----
        x = self.fc(x)

        return x


# =============================
# DATA TRANSFORMS
# =============================
transform = transforms.Compose([
    transforms.Resize((64, 64)),          # resize image
    transforms.ToTensor(),                # image → tensor
    transforms.Normalize((0.1307,), (0.3081,))
    # Alternative normalization:
    # transforms.Normalize(mean, std)
])


# =============================
# DATASET & DATALOADER
# =============================
train_dataset = datasets.MNIST(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True
    # num_workers=2
)


# =============================
# TRAINING SETUP
# =============================
model = SimpleCNN().to(device)

# -------- LOSS FUNCTIONS --------
criterion = nn.CrossEntropyLoss()   # multi-class classification
# criterion = nn.MSELoss()
# criterion = nn.L1Loss()
# criterion = nn.BCELoss()

# -------- OPTIMIZERS --------
optimizer = optim.Adam(model.parameters(), lr=0.001)
# optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
# optimizer = optim.RMSprop(model.parameters(), lr=0.001)
# optimizer = optim.Adagrad(model.parameters(), lr=0.01)


# =============================
# TRAINING LOOP
# =============================
num_epochs = 5

for epoch in range(num_epochs):
    model.train()   # training mode

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        # ----- ZERO GRADIENTS -----
        optimizer.zero_grad()

        # ----- FORWARD PASS -----
        outputs = model(images)

        # ----- LOSS -----
        loss = criterion(outputs, labels)

        # ----- BACKPROPAGATION -----
        loss.backward()

        # ----- UPDATE WEIGHTS -----
        optimizer.step()

        # ----- METRICS -----
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = 100 * correct / total

    print(f"Epoch [{epoch+1}/{num_epochs}] "
          f"Loss: {epoch_loss:.4f}, "
          f"Accuracy: {epoch_acc:.2f}%")


# =============================
# EVALUATION (EXAM PATTERN)
# =============================
model.eval()
with torch.no_grad():
    pass  # evaluation loop here


# =============================
# SAVING & LOADING (EXAM)
# =============================
# torch.save(model.state_dict(), "model.pth")
# model.load_state_dict(torch.load("model.pth"))
