class NeuralNet(nn.Module):

    def init(self, input_size ,hidden_size , num_classes):
        super(NeuralNet, self).init()
        self.l1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.l2 = nn.Linear(hidden_size, num_classes)

    def forward(self, x):
        x = self.l1(x)
        x = self.relu(x)
        x = self.l2(x)
        return x


model = NeuralNet(input_size, hidden_size, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)


n_total_steps = len(train_loader)
#train
for epoch in range(num_epochs):
    for i , (images, labels) in enumerate(train_loader):
        images = images.reshape(-1, 2828).to(device)
        labels = labels.to(device)

        #forward
        outputs = model(images)
        loss = criterion(outputs, labels)

        #backward

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()


        if (i+1) % 100 == 0:
            print (f'epoch {epoch+1} / {num_epochs} , step {i+1} / {n_total_steps} , loss = {loss.item():.4f}')
#test


with torch.no_grad():
    n_correct = 0 
    n_samples = 0 


    for images , labels in test_loader:
        images = images.reshape(-1, 2828).to(device)
        labels = labels.to(device)
        outputs = model(images)


        _, predicted = torch.max(outputs, 1)

        n_samples += labels.shape[0]

        n_correct += (predicted == labels).sum().item()


    acc = 100.0 * n_correct / n_samples
    print(f'accuracy = {acc} ')