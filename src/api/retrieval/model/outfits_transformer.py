from collections import OrderedDict

import numpy as np
import torch
import torch.nn as nn


class LayerNorm(nn.LayerNorm):
    def forward(self, x: torch.Tensor):
        orig_type = x.dtype
        ret = super().forward(x.type(torch.float32))
        return ret.type(orig_type)


class QuickGELU(nn.Module):
    def forward(self, x: torch.Tensor):
        return x * torch.sigmoid(1.702 * x)


class ResidualAttentionBlock(nn.Module):
    def __init__(self, d_model: int, n_head: int, dropout: float):
        super().__init__()

        self.attn = nn.MultiheadAttention(d_model, n_head, dropout=0.2, batch_first=True)
        self.attn_mask = None
        self.ln_1 = LayerNorm(d_model)
        self.mlp = nn.Sequential(
            OrderedDict(
                [
                    ("c_fc", nn.Linear(d_model, d_model * 4)),
                    ("gelu", QuickGELU()),
                    ("c_proj", nn.Linear(d_model * 4, d_model)),
                ]
            )
        )
        self.ln_2 = LayerNorm(d_model)

    def set_attn_mask(self, attn_mask: torch.Tensor):
        self.attn_mask = attn_mask.to(dtype=bool)

    def attention(self, x: torch.Tensor, attn_mask: torch.Tensor):
        attn_mask = attn_mask.to(device=x.device) if attn_mask is not None else None
        out, mask = self.attn(x, x, x, attn_mask=attn_mask)
        return out

    def forward(self, x: torch.Tensor):
        x = x + self.attention(self.ln_1(x), self.attn_mask)
        x = x + self.mlp(self.ln_2(x))
        return x


class Encoder(nn.Module):
    def __init__(
        self, n_categories: int, d_model: int, n_heads: int, n_layers: int, dropout: float
    ):
        super().__init__()
        self.n_heads = n_heads

        self.positional_embeddings = nn.Parameter(torch.empty(1, n_categories + 1, d_model))
        nn.init.normal_(self.positional_embeddings, std=0.02)

        self.blank_embeddings = nn.Parameter(torch.empty(1, 1, d_model))
        nn.init.normal_(self.blank_embeddings, std=0.02)

        self.padding_embeddings = nn.Parameter(torch.empty(1, 1, d_model))
        nn.init.normal_(self.padding_embeddings, std=0.02)

        self.cls_embeddings = nn.Parameter(torch.empty(1, 1, d_model))
        nn.init.normal_(self.cls_embeddings, std=0.02)

        self.encoders = [ResidualAttentionBlock(d_model, n_heads, dropout) for _ in range(n_layers)]
        self.transformer = nn.Sequential(*self.encoders)
        self.ln_post = LayerNorm(d_model)

        self.cls_head = nn.Sequential(
            OrderedDict([("cls_dropout", nn.Dropout(p=0.5)), ("cls_head", nn.Linear(d_model, 2))])
        )

    def forward(self, embeddings, input_mask, target_mask):
        embeddings = torch.where(
            ~input_mask[:, :, None] & ~target_mask[:, :, None], self.padding_embeddings, embeddings
        )
        embeddings = torch.where(target_mask[:, :, None], self.blank_embeddings, embeddings)

        # Add cls embeddings
        cls_embeddings_1 = self.cls_embeddings.expand(embeddings.shape[0], -1, -1)
        cls_embeddings_1 = torch.cat((cls_embeddings_1, embeddings), 1)

        # Add positional encoding
        cls_embeddings_1 = cls_embeddings_1 + self.positional_embeddings

        out_1 = self.transformer(cls_embeddings_1)
        out_1 = self.ln_post(out_1)
        out_1 = out_1[:, 1:, :]

        out_embeddings = torch.where(target_mask[:, :, None], out_1, embeddings)
        return out_embeddings


class OutfitsTransformer(nn.Module):
    def __init__(
        self, n_categories: int, d_model: int, n_heads: int, n_layers: int, dropout: float
    ):
        super().__init__()
        self.encoder = Encoder(n_categories, d_model, n_heads, n_layers, dropout)

    def forward(self, embeddings, input_mask, target_mask):
        out = self.encoder(embeddings, input_mask, target_mask)
        return out

    def __str__(self):
        model_parameters = filter(lambda p: p.requires_grad, self.parameters())
        params = sum([np.prod(p.size()) for p in model_parameters])
        return super().__str__() + f'\nTrainable parameters: {params}'


class OutfitsTransformerModule:
    def __init__(self, pretrained_path, device):
        self.device = device
        self.model = OutfitsTransformer(11, 640, 8, 6, 0.0).to(device)
        state_dict = torch.load(pretrained_path, map_location=device)
        self.model.load_state_dict(state_dict)
        self.model.eval()

    def __call__(self, embedding, input_mask):
        _embedding = embedding.to(self.device).unsqueeze(0)
        _input_mask = input_mask.to(self.device).unsqueeze(0)
        _target_mask = ~_input_mask
        output = self.model(_embedding, _input_mask, _target_mask)
        return output.squeeze(0)
