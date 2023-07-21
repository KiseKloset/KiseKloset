import io
import time
from typing import Union
import random

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
    ref_image: Union[UploadFile, None] = None, caption: str = Form(""), style: int = Form(TON_SUR_TON), request: Request = None
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

    target_image_index = query_top_k_items(target_embedding, None, 1, api_content)[0]
    if len(caption) == 0:
        target_category = "tops" # "default"
    else:
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
    target_image_indices = query_top_k_items(target_embedding, target_category, n_items, api_content)

    for index in target_image_indices:
        assert get_category(index, api_content) == target_category
        item_name = get_item_name(index, api_content)
        item_url = item_name_to_url(item_name, request.app)
        response["Target " + target_category].append({"id": item_name, "url": item_url})

    end = time.time()
    print("Query target images:", end - start)
    start = end

    # OCIR task
    target_image_path = item_name_to_path(item_name, request.app)
    target_image = PIL.Image.open(target_image_path).convert("RGB")
    comp_embeddings = ocir(target_image, target_category, api_content)

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
        random.shuffle(image_indices)
        for index in image_indices[:5]:
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
