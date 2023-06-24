function fill_samples(samples) {
    const container = document.getElementById("sample-container");

    samples.forEach(sample => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("hover-zoom");
        wrapper.classList.add("bg-image");
        wrapper.classList.add("mb-3");
        wrapper.style.width = "40%";

        const image = document.createElement("img");
        image.classList.add("img-fluid");
        image.classList.add("image");
        image.style.aspectRatio = "3 / 4";
        image.src = sample; 

        wrapper.appendChild(image);
        container.appendChild(wrapper);
    })
}


const samples = []
for (let i = 0; i < 18; ++i) {
    samples.push("img/person.jpg");
}

fill_samples(samples)