from pathlib import Path

import gdown
import torch


def gdrive_download(url, output):
    file = Path(output)

    if not file.exists():
        gdown.download(url, output)


def url_download(url, output):
    file = Path(output)

    if not file.exists():
        torch.hub.download_url_to_file(url, output)
