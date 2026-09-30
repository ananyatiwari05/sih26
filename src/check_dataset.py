from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = ROOT / "data" / "prepared" / "images"
MASK_DIR = ROOT / "data" / "prepared" / "masks"


images = sorted(IMAGE_DIR.glob("*.npy"))

if not images:
    raise RuntimeError("No prepared images found.")


# Find a tile that actually contains buildings
candidates = []

for image_path in images:
    mask_path = MASK_DIR / image_path.name

    if not mask_path.exists():
        continue

    mask = np.load(mask_path)
    building_pixels = int(np.sum(mask))

    candidates.append((building_pixels, image_path))


candidates.sort(reverse=True)

building_pixels, image_path = candidates[0]
mask_path = MASK_DIR / image_path.name

image = np.load(image_path)
mask = np.load(mask_path)

image = image.transpose(1, 2, 0)

print("Selected tile:", image_path.name)
print("Image shape:", image.shape)
print("Mask shape:", mask.shape)
print("Building pixels:", building_pixels)
print("Building percentage:", 100 * np.mean(mask))

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].imshow(image)
axes[0].set_title("Image")
axes[0].axis("off")

axes[1].imshow(mask, cmap="gray")
axes[1].set_title("Building Mask")
axes[1].axis("off")

axes[2].imshow(image)
axes[2].imshow(mask, alpha=0.4, cmap="Reds")
axes[2].set_title("Overlay")
axes[2].axis("off")

plt.tight_layout()
plt.show()