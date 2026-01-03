import numpy as np      # Numerical operations
import pandas as pd  # Data manipulation, table operations
import matplotlib.pyplot as plt  # Plotting
import seaborn as sns  # pretty plotting
import torch  # PyTorch library, deep learning framework
import torch.nn as nn  # Neural network modules
import torch.optim as optim  # Optimization algorithms
from torch.utils.data import DataLoader, TensorDataset  #splitting data into batches, shuffling, etc.
from sklearn.datasets import load_iris  # sklearn for loading,splitting, scaling , evaluating performance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def load_data():
    """Load the Iris dataset and convert to DataFrame"""
    print("Step 1: Loading Iris dataset...")
    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    df['target'] = iris.target # Add target column, 
    df['species'] = df['target'].map({0: 'setosa', 1: 'versicolor', 2: 'virginica'}) #target column er value gulo ke species name e map kora
    
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"\nFirst few rows:\n{df.head()}")
    return df, iris.target_names #target name er bhitore 0,1,2 er corresponding species name gulo ache

def preprocess_data(df):
    """Handle nulls, duplicates, and prepare features"""
    print("\n" + "="*50)
    print("Step 2: Preprocessing data...")
    
    # Check for null values
    null_count = df.isnull().sum().sum() # 1st sum for each column, 2nd sum for total
    print(f"Null values found: {null_count}")
    if null_count > 0:
        df = df.dropna() # Drop rows with null values
        print("Null values removed")
    
    # Check for duplicates
    duplicate_count = df.duplicated().sum()
    print(f"Duplicate rows found: {duplicate_count}")
    if duplicate_count > 0:
        df = df.drop_duplicates()
        print("Duplicates removed")
    
    # Separate features and target
    X = df.drop(['target', 'species'], axis=1) #drop mane holo oi column gulo ke feature theke remove kora
    y = df['target']
    
    print(f"Final dataset: {X.shape[0]} samples, {X.shape[1]} features") #target species baade
    return X, y

def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into training and testing sets"""
    print("\n" + "="*50)
    print("Step 3: Splitting data...")
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y #stratify mane holo target variable er distribution maintain kora training ar testing set e
    )   #random state = 42 mane holo je kono bar code run korleo same result pawa jabe, 41 dile onno result pawa jabe
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Testing set: {X_test.shape[0]} samples")
    return X_train, X_test, y_train, y_test

def normalize_data(X_train, X_test):
    """Normalize features using StandardScaler"""
    print("\n" + "="*50)
    print("Step 4: Normalizing data...")
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Data normalized (mean=0, std=1)")
    print(f"Training data mean: {X_train_scaled.mean():.4f}")
    print(f"Training data std: {X_train_scaled.std():.4f}")
    return X_train_scaled, X_test_scaled, scaler

class MLP(nn.Module): #() mane holo nn.Module theke inherit kora
    """Multi-Layer Perceptron for classification"""
    def __init__(self, input_size, hidden_size1, hidden_size2, num_classes):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1) #first fully connected layer (size of input, size of output)
        self.relu1 = nn.ReLU() #activation function
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size2, num_classes) #output layer, num_classes = 3 for iris dataset
    
    def forward(self, x): #If I give you input x, how do you compute the output?
        out = self.fc1(x)
        out = self.relu1(out)
        out = self.fc2(out)
        out = self.relu2(out)
        out = self.fc3(out)
        return out #PyTorch automatically handles backpropagation.

def train_model(X_train, y_train, input_size=4, hidden_size1=10, hidden_size2=5, 
                num_classes=3, num_epochs=100, learning_rate=0.01, batch_size=16):
    """Train a PyTorch MLP classifier"""
    print("\n" + "="*50)
    print("Step 5: Training PyTorch MLP model...")
    
    # Convert to PyTorch tensors #PyTorch only works with tensors, not NumPy arrays.
    X_train_tensor = torch.FloatTensor(X_train) #X_train numopy array, y_train pandas series
    y_train_tensor = torch.LongTensor(y_train.values)
    
    # Create DataLoader
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor) 
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True) #shuffle mane holo data gulo ke random order e niye asha  #batch size mane holo koyta sample niye ekbar e model ke update kora hobe
    
    # Initialize model
    model = MLP(input_size, hidden_size1, hidden_size2, num_classes)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss() #Loss: “How wrong am I?”
    optimizer = optim.Adam(model.parameters(), lr=learning_rate) #Optimization: “How do I adjust my weights to be less wrong?”
                #Adam is an advanced version of gradient descent. full form = Adaptive Moment Estimation.
    print(f"Model architecture: Input({input_size}) -> Hidden({hidden_size1}) -> Hidden({hidden_size2}) -> Output({num_classes})")
    print(f"Training for {num_epochs} epochs...") #epoch mane holo puro dataset ekbar diye model ke train kora
    
    # Training loop
    model.train() #model ke training mode e niye asha
    for epoch in range(num_epochs):
        total_loss = 0
        for batch_X, batch_y in train_loader:
            # Forward pass
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            
            # Backward pass and optimization
            optimizer.zero_grad() # Clear previous gradients
            loss.backward() # Compute gradients
            optimizer.step() # Update weights , this is where learning happens
            
            total_loss += loss.item() #item() mane holo tensor theke scalar value ber kora
        
        # Print progress every 20 epochs
        if (epoch + 1) % 20 == 0:
            avg_loss = total_loss / len(train_loader) #len(train_loader) mane holo koyta batch ase
            print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")
    
    print("Model training complete!")
    return model

def evaluate_model(model, X_test, y_test, target_names):
    """Perform inference and evaluate the model"""
    print("\n" + "="*50)
    print("Step 6: Model Inference & Evaluation...")
    
    # Convert to PyTorch tensors
    X_test_tensor = torch.FloatTensor(X_test)
    
    # Make predictions
    model.eval() #model ke evaluation mode e niye asha
    with torch.no_grad(): #gradient calculation off kora
        outputs = model(X_test_tensor)
        _, y_pred = torch.max(outputs, 1) #1 means along rows, returns max value and index, here index is the predicted class
        y_pred = y_pred.numpy()
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Detailed classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=target_names))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print(cm)
    
    return y_pred, accuracy, cm

def plot_confusion_matrix(cm, target_names):
    """Plot confusion matrix as a heatmap"""
    print("\n" + "="*50)
    print("Step 7: Plotting Confusion Matrix...")
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=target_names, 
                yticklabels=target_names,
                cbar_kws={'label': 'Count'})
    plt.title('Confusion Matrix - Iris Classification (PyTorch MLP)', fontsize=14, fontweight='bold')
    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.show()
    print("Confusion matrix plotted!")

def main():
    """Main pipeline execution"""
    print("="*50)
    print("IRIS CLASSIFICATION PIPELINE (PyTorch)")
    print("="*50)
    
    # Step 1: Load data
    df, target_names = load_data()
    
    # Step 2: Preprocess
    X, y = preprocess_data(df)
    
    # Step 3: Split data
    X_train, X_test, y_train, y_test = split_data(X, y)
    
    # Step 4: Normalize
    X_train_scaled, X_test_scaled, scaler = normalize_data(X_train, X_test)
    
    # Step 5: Train model
    model = train_model(X_train_scaled, y_train)
    
    # Step 6: Evaluate
    y_pred, accuracy, cm = evaluate_model(model, X_test_scaled, y_test, target_names)
    
    # Step 7: Plot confusion matrix
    plot_confusion_matrix(cm, target_names)
    
    print("\n" + "="*50)
    print("PIPELINE COMPLETE!")
    print("="*50)

if __name__ == "__main__":
    main()