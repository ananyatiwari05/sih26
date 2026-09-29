from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import SegformerForSemanticSegmentation
from PIL import Image


ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = ROOT / "models" / "segformer_nazar_best"
TEST_DIR = ROOT / "data" / "prepared" / "test"
OUTPUT_DIR = ROOT / "outputs" / "predictions"

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


def normalize_image(image):
    image = torch.from_numpy(image).float()

    mean = torch.tensor(
        [0.485, 0.456, 0.406],
        dtype=torch.float32
    ).view(3, 1, 1)

    std = torch.tensor(
        [0.229, 0.224, 0.225],
        dtype=torch.float32
    ).view(3, 1, 1)

    image = (image - mean) / std

    return image


def create_overlay(image, mask):
    image = np.transpose(image, (1, 2, 0))

    image = np.clip(
        image * 255,
        0,
        255
    ).astype(np.uint8)

    overlay = image.copy()

    building = mask == 1

    overlay[building, 0] = 255
    overlay[building, 1] = 0
    overlay[building, 2] = 0

    result = (
        0.65 * image +
        0.35 * overlay
    ).astype(np.uint8)

    return result


def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Device:", DEVICE)

    model = SegformerForSemanticSegmentation.from_pretrained(
        MODEL_DIR
    )

    model.to(DEVICE)
    model.eval()

    image_files = sorted(
        (TEST_DIR / "images").glob("*.npy")
    )

    print(
        "Test images:",
        len(image_files)
    )

    for image_path in image_files:

        image = np.load(image_path)

        original_image = image.copy()

        image_tensor = normalize_image(image)

        image_tensor = image_tensor.unsqueeze(0).to(
            DEVICE
        )

        with torch.no_grad():

            outputs = model(
                pixel_values=image_tensor
            )

        logits = F.interpolate(
            outputs.logits,
            size=image.shape[-2:],
            mode="bilinear",
            align_corners=False
        )

        probabilities = torch.softmax(
            logits,
            dim=1
        )

        building_probability = (
            probabilities[0, 1]
            .cpu()
            .numpy()
        )

        prediction = (
            building_probability >= 0.5
        ).astype(np.uint8)

        overlay = create_overlay(
            original_image,
            prediction
        )

        Image.fromarray(
            overlay
        ).save(
            OUTPUT_DIR /
            f"{image_path.stem}_overlay.png"
        )

        mask_image = (
            prediction * 255
        ).astype(np.uint8)

        Image.fromarray(
            mask_image
        ).save(
            OUTPUT_DIR /
            f"{image_path.stem}_mask.png"
        )

        probability_image = np.clip(
            building_probability * 255,
            0,
            255
        ).astype(np.uint8)

        Image.fromarray(
            probability_image
        ).save(
            OUTPUT_DIR /
            f"{image_path.stem}_probability.png"
        )

        print(
            f"Processed: {image_path.name} | "
            f"Building pixels: {prediction.sum()} | "
            f"Coverage: {prediction.mean() * 100:.2f}%"
        )

    print()
    print("Inference complete.")
    print(
        "Results:",
        OUTPUT_DIR
    )


if __name__ == "__main__":
    main()