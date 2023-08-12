import io
import random
import time
from typing import Union

import PIL.Image
from fastapi import APIRouter, Form, Request, UploadFile
from fastapi.responses import JSONResponse

from .service import get_category, get_item_name, ocir, query_top_k_items, tgir

router = APIRouter()

TON_SUR_TON = 0
MIX_AND_MATCH = 1


def get_k_of_style(style):
    try:
        if int(style) == MIX_AND_MATCH:
            return 1000
        return 1
    except Exception as e:
        return 1


@router.post("/")
async def image_retrieval(
    ref_image: Union[UploadFile, None] = None,
    caption: str = Form(""),
    style: int = Form(TON_SUR_TON),
    request: Request = None,
):
    print("Request style", style, ", type", type(style))

    if ref_image is not None:
        ref_image_content = await ref_image.read()
        image = io.BytesIO(ref_image_content)
        pil_image = PIL.Image.open(image).convert("RGB")
    else:
        pil_image = PIL.Image.new('RGB', (192, 256), color=(255, 255, 255))

    api_content = request.app.state.retrieval_content

    response = {}

    start = time.time()

    # TGIR task
    target_embedding = tgir(pil_image, caption, api_content)

    end = time.time()
    print("TGIR:", end - start)
    start = end

    if len(caption) == 0:
        target_category = "tops"  # "default"
    else:
        target_image_index = query_top_k_items(target_embedding, None, 1, api_content)[0]
        target_category = get_category(target_image_index, api_content)

    end = time.time()
    print("TGIR query:", end - start)
    start = end

    # Check valid category
    if target_category is None:
        return JSONResponse(content=response, status_code=200)

    # Add TGIR results to response
    response["Target " + target_category] = []
    n_items = len(request.app.state.retrieval_content["categories"]) - 1
    assert n_items == 10
    target_image_indices = retrieve_similar_items(
        target_embedding, target_category, n_items, api_content
    )

    for index in target_image_indices:
        assert get_category(index, api_content) == target_category
        item_name = get_item_name(index, api_content)
        item_url = item_name_to_url(item_name, request.app)
        response["Target " + target_category].append({"id": item_name, "url": item_url})

    end = time.time()
    print("Query target images:", end - start)
    start = end

    # OCIR task
    comp_embeddings = ocir(target_embedding, target_category, api_content)

    end = time.time()
    print("OCIR:", end - start)
    start = end

    style_k = get_k_of_style(style)
    print("Style k", style_k)

    # Add OCIR results to response
    for category, embedding in comp_embeddings.items():
        if category == target_category:
            continue

        response["Comp " + category] = []
        image_indices = query_top_k_items(embedding, category, style_k, api_content)
        for index in [random.choice(image_indices)]:
            assert get_category(index, api_content) == category
            item_name = get_item_name(index, api_content)
            item_url = item_name_to_url(item_name, request.app)
            response["Comp " + category].append({"id": item_name, "url": item_url})

    end = time.time()
    print("Query comp images:", end - start)
    start = end

    return JSONResponse(content=response, status_code=200)


def item_name_to_url(item_name, app):
    return app.state.static_files["prefix"] + f"/images/{item_name}.jpg"


def item_name_to_path(item_name, app):
    return app.state.static_files["directory"] + f"/images/{item_name}.jpg"


def retrieve_similar_items(target_embedding, target_category, n_items, api_content):
    hard_sample_threshold = 10
    near_sample_threshold = 100
    far_sample_threshold = 500
    all_sample_query = 1000
    items = query_top_k_items(target_embedding, target_category, all_sample_query, api_content)

    n_hard_item = n_items // 2 - 1
    hard_items = items[:n_hard_item]
    hard_items = [x for x in hard_items if not is_in_blacklist(x, api_content)]

    n_near_item = (n_items - n_hard_item - 2) + n_hard_item - len(hard_items)
    near_items = items[hard_sample_threshold:near_sample_threshold]
    near_items = random_sample_order(near_items, n_near_item)
    near_items = [x for x in near_items if not is_in_blacklist(x, api_content)]

    n_far_item = n_items - len(hard_items) - len(near_items)
    if n_far_item > 0:
        far_items = items[far_sample_threshold:]
        far_items = random_sample_order(far_items, n_far_item)
    else:
        far_items = []

    print(
        "Similar items:",
        "hard:",
        len(hard_items),
        ", near:",
        len(near_items),
        ", far:",
        len(far_items),
    )
    return [*hard_items, *near_items, *far_items]


def random_sample_order(mylist, sample_size):
    randIndex = random.sample(range(len(mylist)), sample_size)
    randIndex.sort()
    rand = [mylist[i] for i in randIndex]
    return rand


def is_in_blacklist(index, api_content):
    item_name = get_item_name(index, api_content)
    if item_name in ["213636409"]:
        return True
    return False
