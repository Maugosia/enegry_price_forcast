from time import time
import datetime
import torch
import torch.nn as nn
from neural_architectures.gru_net import GRUNet
from data_loading import load_data
from globals import DEVICE
import os
import matplotlib.pyplot as plt
from evaluate_models import plot_evaluation_over_time


def train(training_data_loader, validation_data_loader, folder_path, learning_rate, hidden_dim=256, n_epochs=3, batch=64):
    val_loss_min = 1000000
    val_loss_list = []
    train_loss_list = []

    input_dim = next(iter(training_data_loader))[0].shape[2]
    print(next(iter(training_data_loader))[0].shape)
    output_dim = 1
    n_layers = 2

    model = GRUNet(input_dim, hidden_dim, output_dim, n_layers)
    model.to(DEVICE)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    epoch_times = []
    # Start training loop
    for epoch in range(1, n_epochs + 1):
        start_time = time()
        h = model.init_hidden(batch)
        print("H from init", h.shape)

        avg_loss_train = 0.
        counter_train = 0
        model.train()
        for x, label in training_data_loader:
            counter_train += 1
            h = h.data
            model.zero_grad()
            print("X shape", x.shape)
            print("H shape in loop", h.shape)
            print("H shape in loop", h[0,0,:].reshape(1,256).shape)
            print("Label shape in loop", label.shape)
            out, h = model(x.to(DEVICE).float(), h)
            print("Out shape in loop", out.shape)
            exit()
            loss = criterion(out, label.to(DEVICE).float())
            loss.backward()
            optimizer.step()
            avg_loss_train += loss.item()

        avg_loss_val = 0.
        counter_val = 0
        model.eval()
        for x, label in validation_data_loader:
            counter_val += 1
            h = h.data
            model.zero_grad()

            out, h = model(x.to(DEVICE).float(), h)
            loss = criterion(out, label.to(DEVICE).float())
            avg_loss_val += loss.item()

        if avg_loss_val < val_loss_min:
            val_loss_min = avg_loss_val
            torch.save(model.state_dict(),
                       folder_path + "/GRU_layers_{}_hidden_{}_epoch_{}_batch_{}_history_{}.pt".format(
                           n_layers, hidden_dim, epoch, batch, x_history_length
                       ))

        current_time = time()
        train_loss_list.append(avg_loss_train / len(training_data_loader))
        val_loss_list.append(avg_loss_val / len(validation_data_loader))
        print("Epoch {}/{}, Train Loss: {}, Val Loss: {}".format(epoch,
                                                                 n_epochs,
                                                                 avg_loss_train / len(training_data_loader),
                                                                 avg_loss_val / len(validation_data_loader)))

        epoch_times.append(current_time - start_time)
    print("Total Training Time: {} seconds".format(str(sum(epoch_times))))
    return model, train_loss_list, val_loss_list


if __name__ == "__main__":
    # PARAMS
    lr = 0.1
    batch_size = 64
    x_history_length = 128
    epochs = 10
    path_data = "../day_ahead_data/PGAE_data.csv"
    folder_name = os.path.join("trained_models", datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
    os.makedirs(folder_name)
    print("saving results to folder: ", folder_name)

    # LOAD AND TRAIN
    [train_loader, val_loader, test_loader], label_transform = load_data(path_data, batch_size, x_history_length)
    gru_model, train_losses, val_losses = train(train_loader, val_loader, folder_name, lr,
                                                batch=batch_size, n_epochs=epochs)

    # ANALYZE
    plot_evaluation_over_time([train_losses, val_losses], ["dane treningowe", "dane walidacyjne"],
                              "Krzywe uczenia modelu GRU", "funkcja kosztu")


    plt.show()
