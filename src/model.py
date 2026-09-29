import torch

from transformers import SegformerForSemanticSegmentation


MODEL_NAME = "nvidia/mit-b0"


def create_model():

    id2label = {
        0: "background",
        1: "building"
    }

    label2id = {
        "background": 0,
        "building": 1
    }

    model = SegformerForSemanticSegmentation.from_pretrained(
        MODEL_NAME,
        num_labels=2,
        id2label=id2label,
        label2id=label2id,
        ignore_mismatched_sizes=True
    )

    return model


if __name__ == "__main__":

    model = create_model()

    print(
        f"Parameters: "
        f"{sum(p.numel() for p in model.parameters()):,}"
    )