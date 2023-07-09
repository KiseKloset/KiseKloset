function setup_samples(samples) {
    const container = document.getElementById("sample-container");
	container.innerHTML = '';

	if (samples){
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
}

// Custom onClick function
function handleImageClick(image_url) {
	let dropZoneElement = document.querySelector(".upload-drop-zone");
	let thumbnailElement = dropZoneElement.querySelector("thumb");

	// First time - remove the prompt
	if (dropZoneElement.querySelector("#upload-instruction")) {
		dropZoneElement.querySelector("#upload-instruction").style.display = "none";
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
			samples.push("samples/model/person.jpg");
		}
	}
	else if (type=="garment"){
		for (let i = 0; i < 18; ++i) {
			samples.push("samples/garment/garment.jpg");
		}
	}

	return samples
}


setup_samples(get_sample("model"));
setup_upload_container(1);

///////////////////////////////////////////////////////////////////////////////
// Upload image
function setup_upload_container(step){
	container = document.querySelector("#middle-container");
	const step_instruction = container.querySelector("#step-instruction");
	const upload_instructor = container.querySelector("#upload-instruction");
	upload_instructor.style.display = "block";

	upload_instructor.innerHTML = "Drop file here or click to upload";
	if (step==1){
		step_instruction.innerHTML = "Step 1: Upload your model OR select from list, then click \"Next\"";
	}
	else if (step==2){
		step_instruction.innerHTML = "Step 2: Upload your garment OR select from list, then click \"Next\"";
	}
	else if (step==3){
		step_instruction.innerHTML = "Try-on result";
	}
}

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
		dropZoneElement.querySelector("#upload-instruction").style.display = "none";
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
function setup_textbox(){
	const container = document.querySelector("")
}


///////////////////////////////////////////////////////////////////////////////
// Flow change
let current_step = 1;
let person_image = document.querySelector("#person-frame").querySelector(".image-frame");
let garment_image = document.querySelector("#garment-frame").querySelector(".image-frame");
const control_buttons = document.querySelector("#control-button");
function set_frame(frame, imageSrc){
	frame.innerHTML = '';
	frame.style.backgroundImage = imageSrc;
}

function dataURLtoFile(dataurl, filename) {
    let arr = dataurl.split(','),
        mime = arr[0].match(/:(.*?);/)[1],
        bstr = atob(arr[arr.length - 1]),
        n = bstr.length,
        u8arr = new Uint8Array(n);
    while(n--){
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, {type:mime});
}

function URLtoData(url){
	let dataURL = url.slice(4, -1).replace(/"/g, "");
	return dataURL;
}

control_buttons.addEventListener("click", () => {
	let thumbnailElement = document.querySelector(".upload-drop-zone").querySelector("thumb");
	if (!thumbnailElement) {
		alert("Please upload OR select an image first!");
		return;
	}

	if (current_step == 1) {
		set_frame(person_image, thumbnailElement.style.backgroundImage);
		setup_samples(get_sample("garment"));
		thumbnailElement.remove();

		setup_upload_container(2);
		current_step = 2;
	}

	else if (current_step == 2) {
		set_frame(garment_image, thumbnailElement.style.backgroundImage);
		document.getElementById("sample-container").innerHTML = '';
		setup_samples(null);
		document.querySelector("#upload-instruction").remove();

		person_url = dataURLtoFile(URLtoData(person_image.style.backgroundImage));
		garment_url = dataURLtoFile(URLtoData(garment_image.style.backgroundImage));
		tryOn(thumbnailElement, person_url, garment_url);

		setup_upload_container(3);
		current_step = 3;
	}
});


function tryOn(display_frame, person_url, garment_url) {
    const body = new FormData();
    body.append("person_image", person_url);
    body.append("garment_image", garment_url);

    fetch('/try-on/image', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
        body: body
    }).then(async (response) => {
        let data = await response.json();
        if (data["message"] == "success") {
            display_frame.style.backgroundImage = `url('${data["result"]}')`;
        }
        else {
            window.alert("Something wrong. Please check your input and try again next time");
        }
    })
}