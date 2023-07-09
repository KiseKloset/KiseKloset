import clip
import PIL.Image
import torch
import torch.nn.functional as F
import torchvision
from torch import nn
from torchvision.transforms import CenterCrop, Compose, Normalize, Resize, ToTensor


class Combiner(nn.Module):
    def __init__(self, clip_feature_dim: int, projection_dim: int, hidden_dim: int):
        super().__init__()
        self.text_projection_layer = nn.Linear(clip_feature_dim, projection_dim)
        self.image_projection_layer = nn.Linear(clip_feature_dim, projection_dim)

        self.dropout1 = nn.Dropout(0.5)
        self.dropout2 = nn.Dropout(0.5)

        self.combiner_layer = nn.Linear(projection_dim * 2, hidden_dim)
        self.output_layer = nn.Linear(hidden_dim, clip_feature_dim)

        self.dropout3 = nn.Dropout(0.5)
        self.dynamic_scalar = nn.Sequential(
            nn.Linear(projection_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid(),
        )

        self.logit_scale = 100

    def forward(
        self,
        image_features: torch.tensor,
        text_features: torch.tensor,
        target_features: torch.tensor,
    ) -> torch.tensor:
        predicted_features = self.combine_features(image_features, text_features)
        target_features = F.normalize(target_features, dim=-1)

        logits = self.logit_scale * predicted_features @ target_features.T
        return logits

    def combine_features(
        self, image_features: torch.tensor, text_features: torch.tensor
    ) -> torch.tensor:
        text_projected_features = self.dropout1(F.relu(self.text_projection_layer(text_features)))
        image_projected_features = self.dropout2(
            F.relu(self.image_projection_layer(image_features))
        )

        raw_combined_features = torch.cat((text_projected_features, image_projected_features), -1)
        combined_features = self.dropout3(F.relu(self.combiner_layer(raw_combined_features)))
        dynamic_scalar = self.dynamic_scalar(raw_combined_features)
        output = (
            self.output_layer(combined_features)
            + dynamic_scalar * text_features
            + (1 - dynamic_scalar) * image_features
        )
        return F.normalize(output, dim=-1)


class TargetPad:
    def __init__(self, target_ratio: float, size: int):
        self.size = size
        self.target_ratio = target_ratio

    def __call__(self, image):
        w, h = image.size
        actual_ratio = max(w, h) / min(w, h)
        if (
            actual_ratio < self.target_ratio
        ):  # check if the ratio is above or below the target ratio
            return image
        scaled_max_wh = max(w, h) / self.target_ratio  # rescale the pad to match the target ratio
        hp = max(int((scaled_max_wh - w) / 2), 0)
        vp = max(int((scaled_max_wh - h) / 2), 0)
        padding = [hp, vp, hp, vp]
        return torchvision.transforms.functional.pad(image, padding, 0, 'constant')


class CLIP4CirModule:
    def __init__(self, clip_path, clip_ft_path, comb_path, device):
        self.device = device
        self.clip_model, _ = clip.load(clip_path, device=device, jit=False)
        clip_state_dict = torch.load(clip_ft_path, map_location=device)
        self.clip_model.load_state_dict(clip_state_dict["CLIP"])

        feature_dim = self.clip_model.visual.output_dim
        self.combiner = Combiner(feature_dim, 2560, 5120).to(device)
        combiner_state_dict = torch.load(comb_path, map_location=device)
        self.combiner.load_state_dict(combiner_state_dict["Combiner"])
        self.combiner.eval()

    def __call__(self, image, caption):
        reference_features = self.encode_image(image)
        if len(caption) == 0:
            return reference_features

        text_inputs = clip.tokenize(caption, truncate=True).to(self.device)

        with torch.no_grad():
            text_features = self.clip_model.encode_text(text_inputs)
            predicted_features = self.combiner.combine_features(
                reference_features.unsqueeze(0).float(), text_features.float()
            )

        return predicted_features.squeeze(0)

    def encode_image(self, image):
        input_dim = self.clip_model.visual.input_resolution
        image = self.__targetpad_transform(1.25, input_dim)(image).to(self.device)

        reference_features = self.clip_model.encode_image(image.unsqueeze(0))
        return reference_features.squeeze(0)

    def __targetpad_transform(self, target_ratio: float, dim: int):
        return Compose(
            [
                TargetPad(target_ratio, dim),
                Resize(dim, interpolation=PIL.Image.BICUBIC),
                CenterCrop(dim),
                self.__convert_image_to_rgb,
                ToTensor(),
                Normalize(
                    (0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)
                ),
            ]
        )

    def __convert_image_to_rgb(self, image):
        return image.convert("RGB")
