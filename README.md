<div align="center">
  <p>
    <a align="center" href="http://selab.edu.vn:20440" target="_blank">
      <img width="50%" src="https://raw.githubusercontent.com/KiseKloset/KiseKloset/assets/logo.png"></a>
  </p>
<br>

🤩 We are thrilled to introduce <a href="http://selab.edu.vn:20440">KiseKloset</a>, a virtual try-on experience and personalized outfit recommendations.

With KiseKloset, you can easily try on clothes virtually by uploading your photo and the desired shirt image, instantly visualizing how the outfit would look on you. After the try-on, we take a step further by providing similar items and complementary pieces that may align with your preferences. Additionally, you can describe your preferred style in just a few words, and our AI system will come up with suggestions in the blink of an eye.
</div>
<br>

## <div align="center">📝 Documentation</div>
**⚠️ This repo is no longer maintained.**

**⚠️ About error download link**

We had accidentally deleted these links and couldn't find a way to recover them. You can try these steps to reproduce the download file (not verified):

1) https://drive.google.com/uc?id=1qRP24WngO52MlxXVHOVzhXHql9GlsaUg, which includes 4 models:
- outfit_transformer.pt : [here](https://drive.google.com/file/d/1SrR0npYTRWfU4SzqaX70YRzr5xE4_w4A)
- clip_ft.pt, combiner.pt: [here](https://drive.google.com/drive/folders/1BPE33_XSm33Min0OaGW2Sl9rcddZ-WF-)
- clip.ft: You can remove this model in the code, just use clip.load("RN50x4", jit=False) instead in this [line](https://github.com/KiseKloset/KiseKloset/blob/265a80e8be899f6c2016d910cc222f14935d7ef6/src/api/retrieval/model/clip4cir.py#L86)

2) https://drive.google.com/uc?id=1pNIbQcflAlyUAYypASSy7UfevI4sFcMC:
You can download the original dataset [here](https://github.com/AemikaChow/AiDLab-fAshIon-Data/blob/main/Datasets/cleaned-maryland.md) and move all images into a single folder "images".
In our version, we also remove some invalid images (no metadata, etc), but that should not affect so much.

### 🧰 Install
Clone this repo.
```
git clone https://github.com/KiseKloset/KiseKloset.git
cd KiseKloset
```

Install with `conda` (we provide script `install.sh`)
```
conda create -n kisekloset python=3.10
conda activate kisekloset
bash install.sh
```

### 👨‍💻 Run
Create an `.env` file and config the necessary environment variables (as in `.env.example`). Then run:
```
python src/main.py
```

*Note: The first run may take a long time because of downloading the models.*

## <div align="center">✔️ TODO</div>
- [ ] Support Docker
- [ ] Support Webcam Try-on
- [ ] Responsive UI

