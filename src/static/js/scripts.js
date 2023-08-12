let current_step = 1;

let data_url_pool = {};

function convertImagePathToDataURL(imageElement, imagePath) {
	if (data_url_pool[imagePath]) {
		imageElement.src = data_url_pool[imagePath];
		return;
	}

	const path = imagePath;
	var image = new Image();
	image.src = imagePath;

	var canvas = document.createElement("canvas");
	var context = canvas.getContext("2d");

	image.onload = function() {
		canvas.width = image.width;
		canvas.height = image.height;

		context.drawImage(image, 0, 0);

		var dataURL = canvas.toDataURL("image/jpeg"); // Change "image/jpeg" to the desired image format if needed

		// Assign the data URL to the image_url variable or use it as desired
		var image_url = dataURL;

		// Use the image_url variable here or return it if needed
		imageElement.src = image_url;

		// Caching
		data_url_pool[path] = image_url;
	};
}

let selected_garment_id = "";

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
			image.style.width= "100%";
			image.style.objectFit = "cover";
			image.dataset.id = sample.split('/').slice(-1);
			convertImagePathToDataURL(image, sample);

			image.addEventListener("click", () => {
				if (current_step === 2) {
					selected_garment_id = image.dataset.id;
				}
				handleImageClick(image.src); // Call your custom onClick function with the corresponding index
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
	let samples = [];
	let samplesPath = "static/samples/" + type + "/";
	if (type=="model"){
		let files = ["000020_0.jpg", "000228_0.jpg", "000619_0.jpg", "001387_0.jpg", "002371_0.jpg",
				"002523_0.jpg", "004423_0.jpg", "010057_0.jpg", "014612_0.jpg", "019243_0.jpg"];
		for (let i = 0; i < files.length; ++i) {
			samples.push(samplesPath + files[i]);
		}
	}
	else if (type=="garment"){
		let files = ["000339_1.jpg", "001448_1.jpg", "003749_1.jpg", "005285_1.jpg", "005586_1.jpg",
					"005683_1.jpg", "008771_1.jpg", "009758_1.jpg", "013319_1.jpg", "018047_1.jpg"];
		for (let i = 0; i < files.length; ++i) {
			samples.push(samplesPath + files[i]);
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
	const step_instruction_note = container.querySelector("#step-instruction-note");
	const upload_instructor = container.querySelector("#upload-instruction");
	if (upload_instructor){
		upload_instructor.style.display = "block";
		upload_instructor.innerHTML = "Drop file here or click to upload";
	}

	if (step==1){
		step_instruction.innerHTML = "Upload your model OR select from list, then click \"Next\"";
		step_instruction_note.innerHTML = "Simple or uniform background is preferred";
	}
	else if (step==2){
		step_instruction.innerHTML = "Upload your garment OR select from list, then click \"Next\"";
		step_instruction_note.innerHTML = "We only support virtual try-on top garments,<br/>others may produce bad results";
	}
	else if (step==3){
		step_instruction.innerHTML = "Try-on result";
	}
}

document.querySelectorAll(".upload-drop-zone").forEach((dropZoneElement) => {
	const inputElement = dropZoneElement.querySelector("input");

	dropZoneElement.addEventListener("click", (e) => {
		if (current_step <= 2) {
			inputElement.click();
		}
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
// Flow change
const person_image = document.querySelector("#person-frame").querySelector(".image-frame");
const garment_image = document.querySelector("#garment-frame").querySelector(".image-frame");
const control_buttons = document.querySelector("#control-button");
function set_frame(frame, imageSrc){
	frame.innerHTML = '';
	frame.style.backgroundImage = imageSrc;
	frame.style.backgroundRepeat = "no-repeat"
	frame.style.backgroundSize = "contain";
	frame.style.backgroundPosition = "center";
	frame.style.backgroundColor = "white"
}

function dataURLtoFile(datauURL, filename) {
    let arr = datauURL.split(','),
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
		thumbnailElement.remove();
		uinstruction = document.querySelector("#upload-instruction")
		if (uinstruction){
			uinstruction.remove();
		}

		person_url = dataURLtoFile(URLtoData(person_image.style.backgroundImage));
		garment_url = dataURLtoFile(URLtoData(garment_image.style.backgroundImage));
		tryOn(person_url, garment_url);
		runRecommendation(garment_url, "", TON_SUR_TON);
		setup_upload_container(3);
		current_step = 3;

		control_buttons.style.display = "none";
	}
});


function tryOn(person_url, garment_url) {
	document.getElementById("try-on-loader").style.display = "block";
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
			const old_data = URLtoData(person_image.style.backgroundImage);
			const new_data = data["result"];
			show_before_after_result(old_data, new_data);
			showUpscale(old_data, new_data);
        }
        else {
            window.alert("Something wrong. Please check your input and try again next time");
        }
		document.getElementById("try-on-loader").style.display = "none";
    })
}

///////////////////////////////////
// Upscale
function upscale(frame_element){
	const body = new FormData();
    body.append("image", dataURLtoFile(frame_element.src));
	fetch('/upscale/image', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
        body: body
    }).then(async (response) => {
        let data = await response.json();
        if (data["message"] == "success") {
			frame_element.src = data["result"];
        }
        else {
            window.alert("Something wrong. Please check your input and try again next time");
        }
    })
}

function showUpscale(before_data, after_data){
	upscale(document.getElementById("result-before"));
	upscale(document.getElementById("result-after"));
}
///////////////////////////////////
// After-before effect

let current_slider = null;

function show_before_after_result(before_data, after_data) {
	current_slider = null;
	can_upload = false;

	const upload_container = document.getElementById("upload-zone");
	const thumbnailElement = upload_container.querySelector("thumb");
	if (thumbnailElement) {
		thumbnailElement.remove()
	}
	upload_container.disabled = true;

	show(document.getElementById("result-before-container"));
	document.getElementById("result-before").src = before_data;

	show(document.getElementById("result-after-container"));
	document.getElementById("result-after").src = after_data;

	show(document.getElementById("result-slider"));
	current_slider = new BeforeAfter("upload-zone");
}

function show(element) {
	element.style.display = "block";
}

/////////////////////////////////////
// Recommendation

let compCache = {};

function runRecommendation(garment_url, caption, style) {
	document.getElementById("retrieval-loader").style.display = "block";
	compCache = {};
	data_url_pool = {};
    const body = new FormData();
    body.append("ref_image", garment_url);
    body.append("caption", caption);
	body.append("style", style);
	const styleHash = 0 * NUM_STYLE + style;
	fetch('/retrieval', {
		method: 'POST',
        headers: {
            'Accept': 'application/json',
        },
        body: body
	}).then(async (response) => {
        const data = await response.json();
		compCache[styleHash] = data;
		const results = parseResults(data);
		showResults(results);
		document.querySelector("#sample-container").style.display = "none";
		document.querySelector("#caption-form").style.display = "block";
		document.querySelector("#caption-button").style.display = "block";
		document.querySelector("#reset-button").style.display = "block";

		document.getElementById("retrieval-loader").style.display = "none";

		const caption_area = document.querySelector("#caption-textarea");
		if (!caption_area.value.length) {
			caption_area.value = "Top garments with the same color or texture";
		}
	})
}

function runCompRecommendation(index, garment_url, style) {
	document.getElementById("retrieval-loader").style.display = "block";
	const styleHash = index * NUM_STYLE + style;
	if (compCache[styleHash] == undefined) {
		const body = new FormData();
		body.append("ref_image", garment_url);
		body.append("caption", "");
		body.append("style", style);

		fetch('/retrieval', {
			method: 'POST',
			headers: {
				'Accept': 'application/json',
			},
			body: body
		}).then(async (response) => {
			const data = await response.json();
			compCache[styleHash] = data;
			const results = parseResults(data);
			showCompResult("inter-results", results.inter);

			document.getElementById("retrieval-loader").style.display = "none";
		})
	} else {
		const results = parseResults(compCache[styleHash]);
		showCompResult("inter-results", results.inter);
		document.getElementById("retrieval-loader").style.display = "none";
	}
}

function parseResults(data) {
	const results = {
		"intra": [],
		"inter": []
	}
	for (let i in data) {
		if (i.startsWith("Target ")) {
			for (let item in data[i]) {
				const url = data[i][item]["url"];
				if (selected_garment_id.length == 0 || !url.includes(selected_garment_id)) {
					results.intra.push(url);
				}
			}
		} else {
			results.inter.push(data[i][0]["url"]);
		}
	}
	return results;
}

function showResults(results) {
	document.getElementById("retrieval-container").style.display = "block";
	showSimilarResult("intra-results", results.intra, results.intra.length >= results.inter.length);
	showCompResult("inter-results", results.inter);
}

function showSimilarResult(containerId, results, shouldPop) {
	const container = document.getElementById(containerId);
	container.innerHTML = '';

	if (results){
		results.unshift("original");
		if (shouldPop) {
			results.pop();
		}

		let i = -1;
		results.forEach(sample => {
			i += 1;
			const wrapper = createItemRecommendationWrapper();
			const image = createItemRecommendationImage(true);

			if (sample === "original") {
				image.src = URLtoData(garment_image.style.backgroundImage);
			} else {
				convertImagePathToDataURL(image, sample);
			}

			wrapper.appendChild(image);
			wrapper.id = "comp-" + i;
			container.appendChild(wrapper);
			wrapper.dataset.id = sample.split("/").slice(-1);

			wrapper.addEventListener("click", (e) => {
				const id = parseInt(e.target.parentNode.id.substring(5));
				const backgroundImage = `url('${image.src}')`;
				set_frame(garment_image, backgroundImage);
				let person_url = dataURLtoFile(URLtoData(person_image.style.backgroundImage));
				let garment_url = dataURLtoFile(image.src)
				tryOn(person_url, garment_url);
				runCompRecommendation(id, garment_url, getSelectedStyle());
				hightlight(document.getElementById("intra-results"), id);
				selected_garment_id = wrapper.dataset.id;
			})
		});

		hightlight(container, 0);
	}
}

function showCompResult(containerId, results) {
	const container = document.getElementById(containerId);
	container.innerHTML = '';

	if (results){
		results.forEach(sample => {
			const wrapper = createItemRecommendationWrapper();
			const image = createItemRecommendationImage(false);
			convertImagePathToDataURL(image, sample);
			wrapper.appendChild(image);
			container.appendChild(wrapper);
		});
	}
}

function createItemRecommendationWrapper() {
	const wrapper = document.createElement("div");
	wrapper.classList.add("hover-zoom");
	wrapper.classList.add("bg-image");
	wrapper.classList.add("ps-0");
	wrapper.classList.add("pe-0");
	wrapper.style.width = "10%";
	wrapper.style.position = "relative";
	return wrapper;
}

function createItemRecommendationImage(showCursor) {
	const image = document.createElement("img");
	image.classList.add("img-fluid");
	image.classList.add("image");
	image.style.aspectRatio = "3 / 4";
	if (showCursor) {
		image.style.cursor = "pointer";
	}
	image.style.objectFit = "cover";
	image.style.width= "100%";
	return image;
}

let highlightIndex = 0;

function hightlight(container, childIndex) {
	for (let i = 0; i < container.children.length; i++) {
		container.children[i].style.setProperty('box-shadow', '');
		container.children[i].style.marginLeft = "0px";
		container.children[i].style.marginRight = "0px";
	}
	highlightIndex = childIndex;
	container.children[childIndex].style.setProperty('box-shadow', '0px 0px 7px 0px rgba(0,255,255,0.7), 0px 0px 14px 0px rgba(0,255,255,0.7), 0px 0px 28px 0px rgba(0,255,255,0.7), 0px 0px 56px 0px rgba(0,255,255,0.7)', 'important');
}

document.querySelector("#caption-button").addEventListener("click", () => {
	const garment_url = dataURLtoFile(URLtoData(garment_image.style.backgroundImage));
	runRecommendation(garment_url, document.querySelector("#caption-textarea").value, getSelectedStyle());
});

// Run recommendation on enter in textarea

function submitOnEnter(event) {
    if (event.which === 13) {
        if (!event.repeat) {
			const garment_url = dataURLtoFile(URLtoData(garment_image.style.backgroundImage));
			runRecommendation(garment_url, document.querySelector("#caption-textarea").value, getSelectedStyle());
        }
        event.preventDefault(); // Prevents the addition of a new line in the text field
    }
}
document.getElementById("caption-textarea").addEventListener("keydown", submitOnEnter);

// Complementary checkbox
const TON_SUR_TON = 0;
const MIX_AND_MATCH = 1;
const NUM_STYLE = 2;

function getSelectedStyle() {
	let e = document.querySelector("input[type='radio'][name=flexRadioDefault]:checked");
	if (!e) {
		return TON_SUR_TON;
	}

	let id = e.id;
	if (id === "flexRadioDefault2") {
		return MIX_AND_MATCH;
	}
	return TON_SUR_TON;
}

let prev = null;
document.querySelectorAll("input[type='radio'][name=flexRadioDefault]").forEach((input) => {
	input.addEventListener('change', function() {
        if (this === prev) {
            return;
        }
		prev = this;

		const garment_url = dataURLtoFile(URLtoData(garment_image.style.backgroundImage));
		runCompRecommendation(highlightIndex, garment_url, getSelectedStyle());
    });
});