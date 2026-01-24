# =====================================
# IMPORTS (STANDARD PYTORCH SET)
# =====================================
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader


# =====================================
# DEVICE SELECTION
# =====================================
# Use GPU if available for faster matrix computations,
# otherwise fall back to CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# =====================================
# MODEL DEFINITION (CNN + FNN)
# =====================================
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()

        # ---------- CONVOLUTION LAYER ----------
        self.conv1 = nn.Conv2d(
            in_channels=1,      
            # 1 because MNIST images are grayscale (single channel)

            out_channels=16,    
            # 16 filters to learn multiple low-level features
            # (edges, corners, textures) without heavy computation

            kernel_size=3,      
            # 3x3 kernels are standard in CNNs
            # They capture local spatial patterns efficiently

            stride=1,           
            # Stride of 1 preserves spatial detail
            # Larger strides would skip information

            padding=1           
            # Padding of 1 ensures output size remains the same
            # Prevents shrinking of feature maps
        )

        # ---------- ACTIVATION FUNCTION ----------
        self.relu = nn.ReLU()
        # ReLU is computationally efficient
        # Introduces non-linearity
        # Prevents vanishing gradient problem

        # ---------- POOLING ----------
        self.pool = nn.MaxPool2d(
            kernel_size=2,
            stride=2
        )
        # 2x2 pooling halves spatial dimensions
        # Reduces computation and overfitting
        # Keeps strongest feature activations

        # ---------- FLATTEN ----------
        self.flatten = nn.Flatten()
        # Converts multi-dimensional tensor into 1D vector
        # Required before fully connected layers

        # ---------- FULLY CONNECTED LAYERS ----------
        self.fc1 = nn.Linear(
            16 * 14 * 14,  
            # 16 feature maps of size 14x14 after pooling
            128
            # 128 neurons balance model capacity and efficiency
        )

        self.fc2 = nn.Linear(
            128,
            10
            # 10 output neurons for digits 0–9
        )


    def forward(self, x):
        # ----- CONVOLUTION -----
        x = self.conv1(x)

        # ----- NON-LINEARITY -----
        x = self.relu(x)

        # ----- DOWNSAMPLING -----
        x = self.pool(x)

        # ----- FLATTEN -----
        x = self.flatten(x)
        # alternative: x = x.view(x.size(0), -1)

        # ----- FULLY CONNECTED -----
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)

        return x


# =====================================
# DATA TRANSFORMATION
# =====================================
transform = transforms.Compose([
    transforms.ToTensor(),
    # Converts image to tensor and scales values to [0,1]

    transforms.Normalize(
        (0.1307,),  
        # Mean of MNIST dataset
        (0.3081,)   
        # Standard deviation of MNIST dataset
        # Normalization improves convergence and stability
        
    )
])


# =====================================
# DATASET & DATALOADER
# =====================================
train_dataset = datasets.MNIST(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    # Batch size of 32 provides a good trade-off
    # between convergence stability and memory usage

    shuffle=True
    # Shuffling prevents the model from learning data order
)


# =====================================
# TRAINING SETUP
# =====================================
model = Net().to(device)

# ---------- LOSS FUNCTION ----------
criterion = nn.CrossEntropyLoss()
# Used for multi-class classification
# Internally applies Softmax + Log loss

# ---------- OPTIMIZER ----------
optimizer = optim.Adam(
    model.parameters(),
    lr=0.001
    # Learning rate 0.001 is standard for Adam
    # Too large → unstable training
    # Too small → slow convergence
)

# Alternative optimizer (exam):
# optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)
# lr=0.01 is common for SGD
# momentum=0.9 accelerates convergence and reduces oscillations


# =====================================
# TRAINING LOOP
# =====================================
num_epochs = 5
# 5 epochs allow sufficient learning
# Avoids overfitting and long training time

for epoch in range(num_epochs):

    model.train()  
    # Enables training-specific behavior (Dropout, BatchNorm)

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        # ---- RESET GRADIENTS ----
        optimizer.zero_grad()
        # Prevents gradient accumulation from previous batches

        # ---- FORWARD PASS ----
        outputs = model(images)

        # ---- LOSS COMPUTATION ----
        loss = criterion(outputs, labels)

        # ---- BACKPROPAGATION ----
        loss.backward()
        # Computes gradients using chain rule

        # ---- PARAMETER UPDATE ----
        optimizer.step()
        # Updates weights to minimize loss

        # ---- METRICS ----
        running_loss += loss.item()
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total

    print(
        f"Epoch [{epoch+1}/{num_epochs}] "
        f"Loss: {running_loss:.4f}, "
        f"Accuracy: {accuracy:.2f}%"
    )


# =====================================
# EVALUATION MODE
# =====================================
model.eval()
# Disables dropout and batch normalization updates

with torch.no_grad():
    # Disables gradient tracking to save memory
    pass


# =====================================
# SAVE / LOAD MODEL
# =====================================
# torch.save(model.state_dict(), "model.pth")
# Saves only model parameters (recommended practice)

# model.load_state_dict(torch.load("model.pth"))
# Loads saved parameters
