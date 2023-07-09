import cupy
import torch
import torch.nn.functional as F
import torchvision.transforms as transforms
from PIL import Image

from .models.afwm_test import AFWM
from .models.mobile_unet_generator import MobileNetV2_unet
from .utils.torch_utils import get_ckpt, load_ckpt


class DMVTON:
    def __init__(self, ckpt_path, device, align_corners=True) -> None:
        self.device = device
        self.align_corners = align_corners

        self.warp_model = AFWM(3, align_corners).to(device)
        load_ckpt(self.warp_model, get_ckpt(ckpt_path['warp']))
        self.warp_model.eval()
        self.gen_model = MobileNetV2_unet(7, 4).to(device)
        load_ckpt(self.gen_model, get_ckpt(ckpt_path['gen']))
        self.gen_model.eval()

    def __call__(self, img: Image, clothes: Image, clothes_edge: Image):
        img, clothes, clothes_edge = (
            img.to(self.device),
            clothes.to(self.device),
            clothes_edge.to(self.device),
        )

        clothes_edge = (clothes_edge > 0.5).float()
        clothes = clothes * clothes_edge

        with cupy.cuda.Device(int(self.device.split(':')[-1])):
            flow_out = self.warp_model(img, clothes)
            (
                warped_clothes,
                last_flow,
            ) = flow_out
            warped_edge = F.grid_sample(
                clothes_edge,
                last_flow.permute(0, 2, 3, 1),
                mode='bilinear',
                padding_mode='zeros',
                align_corners=self.align_corners,
            )

        gen_inputs = torch.cat([img, warped_clothes, warped_edge], 1)
        gen_outputs = self.gen_model(gen_inputs)
        p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
        p_rendered = torch.tanh(p_rendered)
        m_composite = torch.sigmoid(m_composite)
        m_composite = m_composite * warped_edge
        p_tryon = warped_clothes * m_composite + p_rendered * (1 - m_composite)

        return p_tryon


def get_transform(train, method=Image.BICUBIC, normalize=True):
    transform_list = []

    base = float(2**4)
    transform_list.append(transforms.Lambda(lambda img: __make_power_2(img, base, method)))

    if train:
        transform_list.append(transforms.Lambda(lambda img: __flip(img, 0)))

    transform_list += [transforms.ToTensor()]

    if normalize:
        transform_list += [transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    return transforms.Compose(transform_list)


def normalize():
    return transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))


def __make_power_2(img, base, method=Image.BICUBIC):
    try:
        ow, oh = img.size  # PIL
    except:
        oh, ow = img.shape  # numpy
    h = int(round(oh / base) * base)
    w = int(round(ow / base) * base)
    if (h == oh) and (w == ow):
        return img
    return img.resize((w, h), method)


def __flip(img, flip):
    if flip:
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    return img
