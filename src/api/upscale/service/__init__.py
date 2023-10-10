from pathlib import Path

import numpy as np
import torch
import torchvision as tv
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from gfpgan import GFPGANer
from PIL import Image

from .realesrgan import RealESRGANer
from .realesrgan.archs.srvgg_arch import SRVGGNetCompact

# def preprocess(pil_img: Image, color='RGB'):
#     img = pil_img.convert(color)
#     torch_img = tv.transforms.ToTensor()(img)
#     return torch_img


# class UpscaleService:
#     def __init__(self, config: str, quantized=False, device='cpu'):
#         self.model = SESR(model_config=config)
#         self.model.from_pretrained(quantized=quantized)
#         self.device = device
#         self.model.to(device)
#         self.model.eval()

#     @torch.no_grad()
#     def __call__(self, pil_img: Image):
#         torch_img = preprocess(pil_img).unsqueeze(0).to(self.device)
#         sr_img = self.model(torch_img)

#         cv_img = sr_img.squeeze(0).permute(1, 2, 0).detach().cpu().numpy()
#         cv_img = np.clip(cv_img * 255, 0., 255.).astype(np.uint8)
#         return cv_img


class UpscaleService:
    def __init__(
        self,
        model_name: str = 'RealESRGAN_x4plus',
        model_path: str = None,
        denoise_strength: float = 0.5,
        outscale: float = 4,
        device: str = 'cpu',
    ):
        self.model_name = model_name
        self.device = device
        self.outscale = outscale
        self.model, netscale, file_url = self._init_model()
        self.model_path = self._init_model_path(model_path, file_url)
        self.dni_weight = self._init_dni(denoise_strength)
        self.upsampler = self._init_upsampler(netscale)
        self.face_enhancer = self._init_face_enhancer()

    @torch.no_grad()
    def __call__(
        self,
        image: Image,
        face_enhance: bool = True,
    ):
        cv_img = np.array(image)
        if face_enhance:
            _, _, output = self.face_enhancer.enhance(
                cv_img, has_aligned=False, only_center_face=False, paste_back=True
            )
        else:
            output, _ = self.upsampler.enhance(cv_img, outscale=self.outscale)
        return output

    def _init_model(self):
        if self.model_name == 'RealESRGAN_x4plus':  # x4 RRDBNet model
            model = RRDBNet(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4
            )
            netscale = 4
            file_url = [
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
            ]
        elif self.model_name == 'RealESRNet_x4plus':  # x4 RRDBNet model
            model = RRDBNet(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4
            )
            netscale = 4
            file_url = [
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth'
            ]
        elif self.model_name == 'RealESRGAN_x4plus_anime_6B':  # x4 RRDBNet model with 6 blocks
            model = RRDBNet(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4
            )
            netscale = 4
            file_url = [
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth'
            ]
        elif self.model_name == 'RealESRGAN_x2plus':  # x2 RRDBNet model
            model = RRDBNet(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2
            )
            netscale = 2
            file_url = [
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
            ]
        elif self.model_name == 'realesr-animevideov3':  # x4 VGG-style model (XS size)
            model = SRVGGNetCompact(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=16, upscale=4, act_type='prelu'
            )
            netscale = 4
            file_url = [
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth'
            ]
        elif self.model_name == 'realesr-general-x4v3':  # x4 VGG-style model (S size)
            model = SRVGGNetCompact(
                num_in_ch=3, num_out_ch=3, num_feat=64, num_conv=32, upscale=4, act_type='prelu'
            )
            netscale = 4
            file_url = [
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-wdn-x4v3.pth',
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth',
            ]
        else:
            raise ValueError(f'Unsupported model name')

        return model, netscale, file_url

    def _init_model_path(self, model_path, file_url):
        if model_path is None:
            model_path = Path('weights') / (self.model_name + '.pth')
            if not model_path.is_file():
                ROOT_DIR = Path(__file__).resolve().parent
                for url in file_url:
                    # model_path will be updated
                    model_path = load_file_from_url(
                        url=url, model_dir=ROOT_DIR / 'weights', progress=True, file_name=None
                    )
        return model_path

    def _init_dni(self, denoise_strength):
        # Use dni to control the denoise strength
        dni_weight = None
        if self.model_name == 'realesr-general-x4v3' and denoise_strength != 1:
            wdn_model_path = self.model_path.replace(
                'realesr-general-x4v3', 'realesr-general-wdn-x4v3'
            )
            model_path = [self.model_path, wdn_model_path]
            dni_weight = [denoise_strength, 1 - denoise_strength]
        return dni_weight

    def _init_upsampler(self, netscale):
        # restorer
        upsampler = RealESRGANer(
            scale=netscale,
            model_path=self.model_path,
            dni_weight=self.dni_weight,
            model=self.model,
            tile=0,
            tile_pad=0,
            pre_pad=0,
            half=True,
            gpu_id=None if self.device == 'cpu' else self.device.split(':')[-1],
        )
        return upsampler

    def _init_face_enhancer(self):
        # Use GFPGAN for face enhancement
        face_enhancer = GFPGANer(
            model_path='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.3.pth',
            upscale=self.outscale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=self.upsampler,
        )
        return face_enhancer
