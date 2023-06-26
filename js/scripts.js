function fill_samples(samples) {
    const container = document.getElementById("sample-container");

    samples.forEach(sample => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("hover-zoom");
        wrapper.classList.add("bg-image");
        wrapper.classList.add("mb-3");
        wrapper.style.width = "50%";
		wrapper.style.position = "relative";

        const image = document.createElement("img");
        image.classList.add("img-fluid");
        image.classList.add("image");
        image.style.aspectRatio = "3 / 4";
		image.style.borderRadius = "7px";
		image.style.cursor = "pointer";
        image.src = sample; 	

		image.addEventListener("click", () => {
            handleImageClick(sample); // Call your custom onClick function with the corresponding index
        });

        wrapper.appendChild(image);
        container.appendChild(wrapper);
    })
}

// Custom onClick function
function handleImageClick(image_url) {
	let dropZoneElement = document.querySelector(".upload-drop-zone");
	let thumbnailElement = dropZoneElement.querySelector("thumb");

	// First time - remove the prompt
	if (dropZoneElement.querySelector("#upload-instruction")) {
		dropZoneElement.querySelector("#upload-instruction").remove();
	}

	// First time - there is no thumbnail element, so lets create it
	if (!thumbnailElement) {
		thumbnailElement = document.createElement("thumb");
		dropZoneElement.appendChild(thumbnailElement);
	}

	thumbnailElement.style.backgroundImage = `url('${image_url}')`;
}


function get_sample(type){
	let samples = []
	if (type=="model"){
		for (let i = 0; i < 18; ++i) {
			samples.push("img/model/person.jpg");
		}
	}
	else if (type=="garment"){
		for (let i = 0; i < 18; ++i) {
			samples.push("img/model/person.jpg");
		}
	}

	return samples
}


fill_samples(get_sample("model"))


///////////////////////////////////////////////////////////////////////////////
// Upload image
document.querySelectorAll(".upload-drop-zone").forEach((dropZoneElement) => {
	const inputElement = dropZoneElement.querySelector("input");

	dropZoneElement.addEventListener("click", (e) => {
		inputElement.click();
	});

	inputElement.addEventListener("change", (e) => {
		if (inputElement.files.length) {
			updateThumbnail(dropZoneElement, inputElement.files[0]);
			inputElement.value = "";
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


function updateThumbnail(dropZoneElement, file) {
	let thumbnailElement = dropZoneElement.querySelector("thumb");

	// First time - remove the prompt
	if (dropZoneElement.querySelector("#upload-instruction")) {
		dropZoneElement.querySelector("#upload-instruction").remove();
	}

	// First time - there is no thumbnail element, so lets create it
	if (!thumbnailElement) {
		thumbnailElement = document.createElement("thumb");
		dropZoneElement.appendChild(thumbnailElement);
	}

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
///////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////
// Flow change
// let current_step = 1;
// const control_buttons = document.querySelector("#control-button");
// control_buttons.addEventListener("click", () => {
// 	let thumbnailElement = document.querySelector(".upload-drop-zone").querySelector("thumb");
// 	if (!thumbnailElement) {
// 		alert("Please upload OR select an image first!");
// 		return;
// 	}

// 	if (current_step == 1) {
// 		let 
// 	}
	

// });