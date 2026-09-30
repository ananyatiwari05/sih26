from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.amp import autocast, GradScaler
from tqdm import tqdm

from dataset import BuildingDataset
from model import create_model


ROOT = Path(__file__).resolve().parent.parent

TRAIN_DIR = ROOT / "data" / "prepared" / "train"
VAL_DIR = ROOT / "data" / "prepared" / "val"
MODEL_DIR = ROOT / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

BATCH_SIZE = 2
EPOCHS = 15
LEARNING_RATE = 6e-5
NUM_WORKERS = 0


def dice_loss(logits, targets):
    probabilities = torch.softmax(logits, dim=1)[:, 1]

    targets = targets.float()

    smooth = 1.0

    intersection = (probabilities * targets).sum(dim=(1, 2))

    denominator = (
        probabilities.sum(dim=(1, 2))
        + targets.sum(dim=(1, 2))
    )

    dice = (
        (2.0 * intersection + smooth)
        / (denominator + smooth)
    )

    return 1.0 - dice.mean()


def combined_loss(logits, targets):
    ce = F.cross_entropy(logits, targets)
    dice = dice_loss(logits, targets)

    return ce + dice


def calculate_metrics(predictions, targets):
    predictions = predictions.bool()
    targets = targets.bool()

    intersection = (predictions & targets).sum().item()
    prediction_area = predictions.sum().item()
    target_area = targets.sum().item()
    union = (predictions | targets).sum().item()

    return intersection, prediction_area, target_area, union


def validate(model, loader):
    model.eval()

    total_loss = 0.0

    total_intersection = 0
    total_prediction_area = 0
    total_target_area = 0
    total_union = 0

    with torch.no_grad():
        for batch in loader:
            images = batch["pixel_values"].to(
                DEVICE,
                non_blocking=True
            )

            masks = batch["labels"].to(
                DEVICE,
                non_blocking=True
            )

            with autocast(
                device_type="cuda",
                enabled=DEVICE.type == "cuda"
            ):
                outputs = model(pixel_values=images)

                logits = F.interpolate(
                    outputs.logits,
                    size=masks.shape[-2:],
                    mode="bilinear",
                    align_corners=False
                )

                loss = combined_loss(logits, masks)

            predictions = logits.argmax(dim=1)

            (
                intersection,
                prediction_area,
                target_area,
                union
            ) = calculate_metrics(
                predictions == 1,
                masks == 1
            )

            total_intersection += intersection
            total_prediction_area += prediction_area
            total_target_area += target_area
            total_union += union

            total_loss += loss.item()

    iou = (
        total_intersection / total_union
        if total_union > 0
        else 0.0
    )

    dice = (
        2 * total_intersection
        / (total_prediction_area + total_target_area)
        if total_prediction_area + total_target_area > 0
        else 0.0
    )

    return (
        total_loss / len(loader),
        iou,
        dice
    )


def main():

    print("Device:", DEVICE)

    if DEVICE.type == "cuda":
        print(
            "GPU:",
            torch.cuda.get_device_name(0)
        )

        print(
            "VRAM:",
            round(
                torch.cuda.get_device_properties(0).total_memory
                / 1024**3,
                2
            ),
            "GB"
        )

    train_dataset = BuildingDataset(
        TRAIN_DIR,
        augment=True
    )

    val_dataset = BuildingDataset(
        VAL_DIR,
        augment=False
    )

    print(
        "Training samples:",
        len(train_dataset)
    )

    print(
        "Validation samples:",
        len(val_dataset)
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=True
    )

    model = create_model()

    model.to(DEVICE)

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=0.01
    )

    scaler = GradScaler(
        "cuda",
        enabled=DEVICE.type == "cuda"
    )

    best_iou = -1.0

    for epoch in range(EPOCHS):

        model.train()

        running_loss = 0.0

        progress = tqdm(
            train_loader,
            desc=f"Epoch {epoch + 1}/{EPOCHS}"
        )

        for batch in progress:

            images = batch["pixel_values"].to(
                DEVICE,
                non_blocking=True
            )

            masks = batch["labels"].to(
                DEVICE,
                non_blocking=True
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            with autocast(
                device_type="cuda",
                enabled=DEVICE.type == "cuda"
            ):

                outputs = model(
                    pixel_values=images
                )

                logits = F.interpolate(
                    outputs.logits,
                    size=masks.shape[-2:],
                    mode="bilinear",
                    align_corners=False
                )

                loss = combined_loss(
                    logits,
                    masks
                )

            scaler.scale(loss).backward()

            scaler.step(optimizer)

            scaler.update()

            running_loss += loss.item()

            progress.set_postfix(
                loss=f"{loss.item():.4f}"
            )

        train_loss = (
            running_loss / len(train_loader)
        )

        val_loss, val_iou, val_dice = validate(
            model,
            val_loader
        )

        print()
        print(f"Epoch {epoch + 1}")
        print(f"Train Loss: {train_loss:.4f}")
        print(f"Val Loss:   {val_loss:.4f}")
        print(f"Val IoU:    {val_iou:.4f}")
        print(f"Val Dice:   {val_dice:.4f}")

        if val_iou > best_iou:

            best_iou = val_iou

            save_path = (
                MODEL_DIR /
                "segformer_nazar_best"
            )

            model.save_pretrained(
                save_path
            )

            print(
                f"Saved best model → {save_path}"
            )

    print()
    print(
        f"Training complete. "
        f"Best validation IoU: {best_iou:.4f}"
    )


if __name__ == "__main__":
    main()