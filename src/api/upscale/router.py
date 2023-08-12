import base64
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from .service import UpscaleService

router = APIRouter()


upscale_service = UpscaleService(
    model_name='RealESRGAN_x4plus',
    model_path=None,
    denoise_strength=0.3,
    outscale=2,
    device='cuda:0',
)


@router.post('/image')
async def upsclae_image(image: UploadFile):
    image_content = await image.read()

    pil_img = Image.open(BytesIO(image_content)).convert('RGB')

    cv_img = upscale_service(pil_img, face_enhance=True)

    if cv_img is not None:
        pil_result = Image.fromarray(cv_img)
    else:
        pil_result = pil_img

    image_buffer = BytesIO()
    pil_result.save(image_buffer, 'JPEG')
    image_buffer.seek(0)

    base64_string = "data:image/jpeg;base64," + base64.b64encode(image_buffer.getvalue()).decode()

    return JSONResponse(
        content={
            'message': 'success',
            'result': base64_string,
        }
    )
