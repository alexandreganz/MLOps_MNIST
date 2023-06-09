import argparse

import matplotlib.pyplot as plt
import torch

from src.data.make_dataset import CorruptMnist
from src.models.model import MyAwesomeModel

import mlflow
import mlflow.pytorch
from mlflow import MlflowClient


def print_auto_logged_info(r):
    tags = {k: v for k, v in r.data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [f.path for f in MlflowClient().list_artifacts(r.info.run_id, "model")]
    print("run_id: {}".format(r.info.run_id))
    print("artifacts: {}".format(artifacts))
    print("params: {}".format(r.data.params))
    print("metrics: {}".format(r.data.metrics))
    print("tags: {}".format(tags))


def training() -> None:
    parser = argparse.ArgumentParser(description="Training arguments")
    parser.add_argument("--lr", default=1e-3)
    args = parser.parse_args()
    print(args)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    model = MyAwesomeModel()
    model = model.to(device)

    train_set = CorruptMnist(train=True, in_folder="data/raw", out_folder="data/processed")
    dataloader = torch.utils.data.DataLoader(train_set, batch_size=128)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    criterion = torch.nn.CrossEntropyLoss()

    n_epoch = 5
    for epoch in range(n_epoch):
        loss_tracker = []
        for batch in dataloader:
            optimizer.zero_grad()
            x, y = batch
            preds = model(x.to(device))
            loss = criterion(preds, y.to(device))
            loss.backward()
            optimizer.step()
            loss_tracker.append(loss.item())
            
        print(f"Epoch {epoch+1}/{n_epoch}. Loss: {loss}")
        

        
        
    torch.save(model.state_dict(), "models/trained_model.pt")

    plt.plot(loss_tracker, "-")
    plt.xlabel("Training step")
    plt.ylabel("Training loss")
    plt.savefig(f"reports/figures/training_curve.png")
    
    
# testing the gcloud trigger
if __name__ == "__main__":
    training()
    
