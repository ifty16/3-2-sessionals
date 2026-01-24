import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader


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
def sgd(model, lr=0.01):
    # 1. Disable gradient tracking for the update
    with torch.no_grad():
        # 2. Loop through every parameter (weight/bias) in the model
        for param in model.parameters():
            if param.grad is not None:
                # 3. Update the parameter (In-place subtraction)
                # param.data -= lr * param.grad
                param.sub_(lr * param.grad)

                # 4. Zero the gradient manually (Important!)
                param.grad.zero_()


def adam(model, state, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
    """
    The Update Function:
    It combines Momentum and RMSProp.
    beta_1 (Beta1): Usually 0.9 (Controls momentum).
    beta_2 (Beta2): Usually 0.999 (Controls velocity).
    epsilon (Epsilon): 1e-8 (Prevents division by zero).
    """
    with torch.no_grad():
        for name, param in model.named_parameters():
            if param.grad is not None:
                # Get gradients
                g = param.grad

                # Get state for this specific parameter
                m = state[name]['m']
                v = state[name]['v']
                state[name]['t'] += 1
                t = state[name]['t']

                # --- ADAM MATH ---
                # 1. Update Momentum (m)
                # m = beta1 * m + (1 - beta1) * g
                m.mul_(beta1).add_(g, alpha=1 - beta1)

                # 2. Update Velocity (v) - Note: g^2
                # v = beta2 * v + (1 - beta2) * g^2
                v.mul_(beta2).addcmul_(g, g, value=1 - beta2)

                # 3. Bias Correction (Fix starts near 0)
                m_hat = m / (1 - beta1 ** t)
                v_hat = v / (1 - beta2 ** t)

                # 4. Update Weights
                # W = W - lr * m_hat / (sqrt(v_hat) + eps)
                update = m_hat / (torch.sqrt(v_hat) + eps)
                param.sub_(lr * update)

                # 5. Zero Gradient
                param.grad.zero_()

                # Save state back (not strictly needed if using in-place ops, but safe)
                state[name]['m'] = m
                state[name]['v'] = v


def train_one_epoch(model, loader):
    # TODO 5: Define Optimizer (Adam, lr=0.001)
    # optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Define Loss (Cross Entropy for classification)
    criterion = nn.CrossEntropyLoss()

    """
    The Concept:Adam is "SGD with memory". It remembers:
    Momentum (m): The moving average of gradients (Direction).
    Velocity (v): The moving average of squared gradients (Speed/Magnitude).
    Because Adam needs "memory" of previous steps (t-1),
    you need a way to store $m$ and v for every single parameter in your model.
    The Setup (Initialize Memory):Need to run this before training starts.
    """
    # Dictionary to hold states
    state = {}

    # Initialize m and v as Zeros for every parameter
    for name, param in model.named_parameters():
        state[name] = {
            'm': torch.zeros_like(param),
            'v': torch.zeros_like(param),
            't': 0 # Time step
        }

    model.train()  # Set mode

    for images, labels in loader:
        # TODO 6: The "5 Magic Lines" of Training

        # A. Reset Gradients
        # optimizer.zero_grad()

        # B. Forward Pass
        outputs = model(images)

        # C. Calculate Loss
        loss = criterion(outputs, labels)

        # D. Backward Pass (Gradients)
        loss.backward()

        # E. Update Weights
        # optimizer.step()
        adam(model, state, lr=0.001)

    print("Epoch complete")


# -------------------------------------------------
# SELF-CHECK (Mental Walkthrough)
# -------------------------------------------------
# If input is 32x32...
# Conv (pad 1) -> 32x32
# Pool (2x2)   -> 16x16
# Channels     -> 32
# Flatten Size -> 32 * 16 * 16 = 8192
