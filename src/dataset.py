from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class BuildingDataset(Dataset):

    def __init__(self, root_dir, augment=False):

        self.root_dir = Path(root_dir)
        self.image_dir = self.root_dir / "images"
        self.mask_dir = self.root_dir / "masks"

        self.files = sorted(self.image_dir.glob("*.npy"))

        self.augment = augment

        if len(self.files) == 0:
            raise RuntimeError(
                f"No images found in {self.image_dir}"
            )

    def __len__(self):
        return len(self.files)

    def __getitem__(self, index):
        image_path = self.files[index]
        mask_path = self.mask_dir / image_path.name

        image = np.load(image_path)
        mask = np.load(mask_path)

        image = torch.from_numpy(image).float()
        mask = torch.from_numpy(mask).long()

        mean = torch.tensor(
            [0.485, 0.456, 0.406],
            dtype=torch.float32
        ).view(3, 1, 1)

        std = torch.tensor(
            [0.229, 0.224, 0.225],
            dtype=torch.float32
        ).view(3, 1, 1)

        image = (image - mean) / std

        if self.augment:

            if torch.rand(1).item() > 0.5:
                image = torch.flip(image, dims=[2])
                mask = torch.flip(mask, dims=[1])

            if torch.rand(1).item() > 0.5:
                image = torch.flip(image, dims=[1])
                mask = torch.flip(mask, dims=[0])

            if torch.rand(1).item() > 0.5:
                k = torch.randint(0, 4, (1,)).item()

                if k > 0:
                    image = torch.rot90(
                        image,
                        k,
                        dims=[1, 2]
                    )

                    mask = torch.rot90(
                        mask,
                        k,
                        dims=[0, 1]
                    )

        return {
            "pixel_values": image,
            "labels": mask
        }