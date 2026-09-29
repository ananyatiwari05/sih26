from pathlib import Path

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.amp import autocast
from tqdm import tqdm

from dataset import BuildingDataset
from transformers import SegformerForSemanticSegmentation

ROOT = Path(__file__).resolve().parent.parent

TEST_DIR = ROOT / "data" / "prepared" / "test"
MODEL_DIR = ROOT / "models" / "segformer_nazar_best"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

BATCH_SIZE = 2


def calculate_metrics(predictions, targets):
    predictions = predictions.bool()
    targets = targets.bool()

    intersection = (
        predictions & targets
    ).sum().item()

    prediction_area = (
        predictions.sum().item()
    )

    target_area = (
        targets.sum().item()
    )

    union = (
        predictions | targets
    ).sum().item()

    return (
        intersection,
        prediction_area,
        target_area,
        union
    )


def main():

    print("Device:", DEVICE)

    test_dataset = BuildingDataset(
        TEST_DIR,
        augment=False
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
        pin_memory=True
    )

    print(
        "Test samples:",
        len(test_dataset)
    )

    model = SegformerForSemanticSegmentation.from_pretrained(
        MODEL_DIR
    )

    model.to(DEVICE)
    model.eval()

    total_intersection = 0
    total_prediction_area = 0
    total_target_area = 0
    total_union = 0

    with torch.no_grad():

        for batch in tqdm(
            test_loader,
            desc="Evaluating"
        ):

            images = batch[
                "pixel_values"
            ].to(
                DEVICE,
                non_blocking=True
            )

            masks = batch[
                "labels"
            ].to(
                DEVICE,
                non_blocking=True
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

            predictions = logits.argmax(
                dim=1
            )

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

    iou = (
        total_intersection /
        total_union
    )

    dice = (
        2 * total_intersection /
        (
            total_prediction_area +
            total_target_area
        )
    )

    print()
    print("==============================")
    print("FINAL TEST RESULTS")
    print("==============================")
    print(
        f"Building IoU : {iou:.4f}"
    )
    print(
        f"Building Dice: {dice:.4f}"
    )
    print(
        f"IoU percentage: {iou * 100:.2f}%"
    )
    print(
        f"Dice percentage: {dice * 100:.2f}%"
    )


if __name__ == "__main__":
    main()