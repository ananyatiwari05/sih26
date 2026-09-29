from pathlib import Path
import json
import numpy as np
import rasterio
import geopandas as gpd

from rasterio.features import rasterize


ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data" / "spacenet_sample"
OUTPUT_DIR = ROOT / "data" / "prepared"

IMAGE_DIR = DATA_DIR / "raw" / "images"
LABEL_DIR = DATA_DIR / "raw" / "labels"
SPLIT_FILE = DATA_DIR / "split.json"

TILE_SIZE = 512
STRIDE = 384


def normalize_image(image):
    image = image.astype(np.float32)

    output = np.zeros_like(image)

    for i in range(image.shape[0]):
        band = image[i]

        valid = band[band > 0]

        if len(valid) == 0:
            continue

        low = np.percentile(valid, 2)
        high = np.percentile(valid, 98)

        if high <= low:
            high = low + 1

        output[i] = np.clip(
            (band - low) / (high - low),
            0,
            1
        )

    return output


def create_mask(label_path, transform, height, width, crs):

    buildings = gpd.read_file(label_path)

    if buildings.empty:
        return np.zeros((height, width), dtype=np.uint8)

    if buildings.crs is not None and buildings.crs != crs:
        buildings = buildings.to_crs(crs)

    geometries = []

    for geometry in buildings.geometry:

        if geometry is None or geometry.is_empty:
            continue

        if geometry.geom_type == "Polygon":
            geometries.append(geometry)

        elif geometry.geom_type == "MultiPolygon":
            geometries.extend(list(geometry.geoms))

    return rasterize(
        [(geometry, 1) for geometry in geometries],
        out_shape=(height, width),
        transform=transform,
        fill=0,
        dtype=np.uint8
    )


def get_positions(length):

    if length <= TILE_SIZE:
        return [0]

    positions = list(
        range(
            0,
            length - TILE_SIZE + 1,
            STRIDE
        )
    )

    final_position = length - TILE_SIZE

    if positions[-1] != final_position:
        positions.append(final_position)

    return positions


def load_split():

    with open(SPLIT_FILE, "r") as f:
        split = json.load(f)

    print("Dataset split:")
    print("Train:", len(split["train"]))
    print("Val:", len(split["val"]))
    print("Test:", len(split["test"]))

    return split


def determine_split(image_name, split):

    image_id = Path(image_name).stem

    if image_id.startswith("img"):
        image_id = image_id[3:]

    for split_name, ids in split.items():

        if image_id in [str(x) for x in ids]:
            return split_name

    raise ValueError(
        f"Could not determine split for {image_name}"
    )

def main():

    split = load_split()

    images = sorted(IMAGE_DIR.glob("*.tif"))

    print(f"\nFound {len(images)} images")

    total_tiles = {
        "train": 0,
        "val": 0,
        "test": 0
    }

    for image_path in images:

        label_path = LABEL_DIR / f"{image_path.stem}.geojson"

        if not label_path.exists():
            print(f"Missing label: {label_path}")
            continue

        split_name = determine_split(
            image_path.name,
            split
        )

        image_output = (
            OUTPUT_DIR /
            split_name /
            "images"
        )

        mask_output = (
            OUTPUT_DIR /
            split_name /
            "masks"
        )

        image_output.mkdir(
            parents=True,
            exist_ok=True
        )

        mask_output.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            f"\nProcessing {image_path.name}"
            f" → {split_name}"
        )

        with rasterio.open(image_path) as src:

            image = src.read()

            mask = create_mask(
                label_path,
                src.transform,
                src.height,
                src.width,
                src.crs
            )

        image = normalize_image(image)

        ys = get_positions(image.shape[1])
        xs = get_positions(image.shape[2])

        for y in ys:

            for x in xs:

                image_tile = image[
                    :,
                    y:y + TILE_SIZE,
                    x:x + TILE_SIZE
                ]

                mask_tile = mask[
                    y:y + TILE_SIZE,
                    x:x + TILE_SIZE
                ]

                if image_tile.shape != (
                    3,
                    TILE_SIZE,
                    TILE_SIZE
                ):
                    continue

                tile_name = (
                    f"{image_path.stem}"
                    f"_{y}_{x}.npy"
                )

                np.save(
                    image_output / tile_name,
                    image_tile.astype(np.float32)
                )

                np.save(
                    mask_output / tile_name,
                    mask_tile.astype(np.uint8)
                )

                total_tiles[split_name] += 1

    print("\n============================")
    print("Dataset preparation complete")
    print("============================")

    print(
        f"Train tiles: {total_tiles['train']}"
    )

    print(
        f"Val tiles: {total_tiles['val']}"
    )

    print(
        f"Test tiles: {total_tiles['test']}"
    )


if __name__ == "__main__":
    main()