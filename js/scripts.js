function fill_samples(samples) {
    const container = document.getElementById("sample-container");

    samples.forEach(sample => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("hover-zoom");
        wrapper.classList.add("bg-image");
        wrapper.classList.add("mb-3");
        wrapper.style.width = "40%";
		wrapper.style.position = "relative";

        const image = document.createElement("img");
        image.classList.add("img-fluid");
        image.classList.add("image");
        image.style.aspectRatio = "3 / 4";
		image.style.borderRadius = "7px";
		image.style.cursor = "pointer";
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


document.querySelectorAll(".upload-drop-zone").forEach((dropZoneElement) => {
	const inputElement = dropZoneElement.querySelector("input");

	dropZoneElement.addEventListener("click", (e) => {
		inputElement.click();
	});

	inputElement.addEventListener("change", (e) => {
		if (inputElement.files.length) {
			updateThumbnail(dropZoneElement, inputElement.files[0]);
		}
	});

	dropZoneElement.addEventListener("dragover", (e) => {
		e.preventDefault();
		dropZoneElement.classList.add("active");
	});

	["dragleave", "dragend"].forEach((type) => {
		dropZoneElement.addEventListener(type, (e) => {
			dropZoneElement.classList.remove("active");
		});
	});

	dropZoneElement.addEventListener("drop", (e) => {
		e.preventDefault();

		if (e.dataTransfer.files.length) {
			inputElement.files = e.dataTransfer.files;
			updateThumbnail(dropZoneElement, e.dataTransfer.files[0]);
		}

		dropZoneElement.classList.remove("active");
	});
});

/**
 * Updates the thumbnail on a drop zone element.
 *
 * @param {HTMLElement} dropZoneElement
 * @param {File} file
 */
function updateThumbnail(dropZoneElement, file) {
	let thumbnailElement = dropZoneElement.querySelector("thumb");

	// First time - remove the prompt
	if (dropZoneElement.querySelector(".upload-drop-zone_instruction")) {
		dropZoneElement.querySelector(".upload-drop-zone_instruction").remove();
	}

	// First time - there is no thumbnail element, so lets create it
	if (!thumbnailElement) {
		thumbnailElement = document.createElement("thumb");
		dropZoneElement.appendChild(thumbnailElement);
	}

	thumbnailElement.dataset.label = file.name;

	// Show thumbnail for image files
	if (file.type.startsWith("image/")) {
		const reader = new FileReader();

		reader.readAsDataURL(file);
		reader.onload = () => {
			thumbnailElement.style.backgroundImage = `url('${reader.result}')`;
		};
	} else {
		thumbnailElement.style.backgroundImage = null;
	}
}