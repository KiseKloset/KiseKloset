import json
import pickle
import sys
from pathlib import Path

import numpy as np
import PIL.Image
import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parent  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH


from model.clip4cir import CLIP4CirModule
from model.outfits_transformer import OutfitsTransformerModule


def preload(device):
    pretrained_dir = ROOT / "pretrained"
    data_dir = ROOT / "dataset"
    content = {}

    # Load models
    content["models"] = {}
    content["models"]["clip4cir"] = CLIP4CirModule(
        pretrained_dir / "clip.pt",
        pretrained_dir / "clip_ft.pt",
        pretrained_dir / "combiner.pt",
        device,
    )
    content["models"]["outfits_transformer"] = OutfitsTransformerModule(
        pretrained_dir / "outfits_transformer.pt", device
    )

    # Load item names
    with open(data_dir / "polyvore_index_names.pkl", "rb") as f:
        content["index_names"] = np.array(pickle.load(f))

    # Load item embeddings
    content["index_embeddings"] = torch.nn.functional.normalize(
        torch.load(data_dir / "polyvore_index_embeddings.pt", map_location=device).type(
            torch.float32
        )
    )

    # Load item metadatas
    content["index_metadatas"] = {}
    with open(data_dir / "polyvore_item_metadata.json") as f:
        data = json.load(f)

        for idx, name in enumerate(content["index_names"]):
            if name in data:
                category = data[name]["semantic_category"]
                content["index_metadatas"][idx] = {"category": category}

    # Load categories
    content["categories"] = [
        "all-body",
        "bags",
        "tops",
        "outerwear",
        "hats",
        "bottoms",
        "scarves",
        "jewellery",
        "accessories",
        "shoes",
        "sunglasses",
    ]

    return content


def tgir(image: PIL.Image.Image, caption: str, api_content: dict):
    return api_content["models"]["clip4cir"](image, caption)


def ocir(image: PIL.Image.Image, category: str, api_content: dict):
    embedding = api_content["models"]["clip4cir"].encode_image(image)

    if category not in api_content["categories"]:
        return {i: [] for i in api_content["categories"]}

    idx = api_content["categories"].index(category)
    mask = torch.full((len(api_content["categories"]),), False)
    mask[idx] = True

    output = api_content["models"]["outfits_transformer"](embedding, mask)
    return dict(zip(api_content["categories"], output))


def query_top_k_items(embedding, category, top_k, api_content: dict):
    device = api_content["index_embeddings"].device
    metadatas = api_content["index_metadatas"]

    if category in api_content["categories"]:
        indices = np.array([i for i in metadatas if metadatas[i]["category"] == category])
    else:
        indices = np.arange(len(api_content["index_embeddings"]))

    index_embeddings = api_content["index_embeddings"][indices]

    embedding = embedding.unsqueeze(0).to(device)
    cos_similarity = embedding @ index_embeddings.transpose(0, 1)
    sorted_indices = torch.topk(cos_similarity, top_k, dim=1, largest=True).indices

    return indices[sorted_indices.flatten().cpu().numpy()]


def get_category(item_index, api_content: dict):
    if item_index in api_content["index_metadatas"]:
        return api_content["index_metadatas"][item_index]["category"]

    return None


def get_item_name(item_index, api_content: dict):
    return api_content["index_names"][item_index]
