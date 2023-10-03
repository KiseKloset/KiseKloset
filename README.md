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

