// Imports
const htmlToText = require("html-to-text")
const toWav = require("audiobuffer-to-wav")

// Constants
const BACKEND_URL = "https://shwast-fun-app.azurewebsites.net/api"
const FIND_MOST_RELEVANT_SECTION = true
const CURRENT_PAGE_HEADING = "CURRENT PAGE"

// Global variables
let history = []

/* Initialise cache for text in scraped pages. 
sessionStorage stores throughout a browser session whereas 
localStorage persists across browser sessions.
Pages are represented by an object {
	location: { // the current page
		url: { // relative URL of a page
			prettyText: // text content of this page,
			summary: // potentially store GPT-summarised text
		},
	}
} 
Note this could be made more efficient in the future*/
sessionStorage["scrapedPages"] = sessionStorage["scrapedPages"] || "{}"

let mediaRecorder
let chunks = []
let showAudioControls = false
let useTTS = false

// Callbacks
document
	.getElementById("search-button")
	.addEventListener("click", async (event) => {
		let inputElement = document.getElementById("user-query")
		let outputElement = document.getElementById("search-result")
		if (inputElement.value == "") {
			return
		}

		document.getElementById("search-result").style.display = "block"

		try {
			outputElement.innerHTML = "Thinking..."
			outputElement.innerHTML = await handleSearch(inputElement.value)
		} catch (err) {
			console.log(err)
			outputElement.innerHTML =
				"Unknown error occured. Please try again later."
		}

		if (useTTS){
			await speakSearchResult()
		}
	})

document
	.getElementById("user-query")
	.addEventListener("keypress", async (event) => {
		if (event.key === "Enter") {
			event.preventDefault()
			document.getElementById("search-button").click()
		}
	})

document
	.getElementById("show-audio-controls-button")
	.addEventListener("click", async (event) => {
		if (!showAudioControls){
			showAudioControls = true
			useTTS = true //eventually add separate button to use TTS
			document.getElementById("show-audio-controls-button").textContent = "Hide audio"
			await speakSearchResult()
			document.getElementById("mic-button").style.display = "block"
		} else {
			showAudioControls = false
			useTTS = false
			document.getElementById("show-audio-controls-button").textContent = "Show audio"
			document.getElementById("mic-button").style.display = "none"
			document.getElementById("audio-player").style.display = "none"
		}
	})

document.getElementById("mic-button").addEventListener("click", () => {
	if (!mediaRecorder) {
		startRecording()
		document.getElementById("mic-button").textContent = "Stop"
	} else {
		mediaRecorder.stop()
		document.getElementById("mic-button").textContent = "Record"
	}
})

async function handleSearch(query) {
	// Don't persist the following as this is very fast
	let relevantPageRawHtml = getCurrentPageRawHtml()
	const scrapedHeadings = scrapeHeadings(relevantPageRawHtml)

	// This is only used for context for select relevant section, and is not cached.
	// However if this requires some slow NLP in future, this will require read/write
	// to cache hopefully using the same cache as below
	const currentPagePrettyText = parseGovTextFromHtml(relevantPageRawHtml)

	const mostRelevantHeading = FIND_MOST_RELEVANT_SECTION
		? await callSelectRelevantSectionBackend(
				query,
				scrapedHeadings,
				currentPagePrettyText
		  )
		: { heading: CURRENT_PAGE_HEADING, url: "" }

	let mostRelevantPage = JSON.parse(sessionStorage["scrapedPages"])[
		window.location.href
	]?.[mostRelevantHeading.url]

	if (!mostRelevantPage) {
		console.log(`Scraping ${mostRelevantHeading.heading}...`)

		relevantPageRawHtml =
			mostRelevantHeading.url == ""
				? relevantPageRawHtml
				: await getExternalPageRawHtml(mostRelevantHeading.url)

		mostRelevantPage = {
			prettyText: parseGovTextFromHtml(relevantPageRawHtml),
			summary: "",
		}

		const storage = JSON.parse(sessionStorage["scrapedPages"])
		storage[window.location.href] ||= {}
		storage[window.location.href][mostRelevantHeading.url] =
			mostRelevantPage

		sessionStorage["scrapedPages"] = JSON.stringify(storage)
	}

	const answer = await callQueryBackend(mostRelevantPage.prettyText, query)

	var query_dict = {}
	query_dict.role = "user"
	query_dict.content = query
	
	var answer_dict = {}
	answer_dict.role = "assistant"
	answer_dict.content = answer


	history.push(query_dict)
	history.push(answer_dict)
	
	return formatSearchResult(answer, mostRelevantHeading)
}

function getCurrentPageRawHtml() {
	return window.parent.document.body.outerHTML
}

async function getExternalPageRawHtml(url) {
	const response = await fetch(url)
	const htmlString = await response.text()
	return htmlString
}

function scrapeHeadings(rawHtml) {
	const headings = htmlToText.convert(rawHtml, {
		wordwrap: false,
		baseElements: {
			selectors: [
				"nav.gem-c-contents-list", // GOV.UK "Contents" list
				"nav.beta-nhsuk-navigation-sideways", // NHS.UK child page "More in..." list
				"ul.nhsuk-hub-key-links", // NHS.UK parent page "Contents" list
			],
			returnDomByDefault: false,
		},
	})
	//TODO logic to check if headings empty or rows are have certain length etc
	const headingsList = headings
		.split("\n")
		.map((x) => x.split(/[*]|[0-9]+\.|[[]|[]]/g))
		.filter((x) => x.length > 1)
		.concat([["", CURRENT_PAGE_HEADING]])
		.reduce(
			(acc, x) => ({
				...acc,
				[x[1].trim()]: x.length < 3 ? "" : x[2].replace(/[\[\]]/g, ""),
			}),
			{}
		)

	return headingsList
}

function parseGovTextFromHtml(rawHtml) {
	const prettyText = htmlToText.convert(rawHtml, {
		baseElements: {
			selectors: ["div.govuk-govspeak", "article"],
			returnDomByDefault: false,
		},
		selectors: [
			{
				selector: "a",
				options: { ignoreHref: true },
			},
		],
	})
	return prettyText
}

function formatSearchResult(answer, relevantHeading) {
	const citation =
		relevantHeading.heading == CURRENT_PAGE_HEADING
			? "the current page"
			: `<a href="${relevantHeading.url}" target="_blank">${relevantHeading.heading}</a>`
	return `${answer}<br><small><i>The information above has been taken from ${citation}</i></small>.`
}

async function callQueryBackend(context, query) {
	const response = await fetch(`${BACKEND_URL}/chatgpt`, {
		method: "post",
		headers: {
			"Content-type": "application/json",
		},
		body: JSON.stringify({
			context: context,
			query: query,
			history: history
		}),
	})

	const responseJson = await response.json()
	const output = responseJson["output"]
	console.log(`Query: ${query}`)
	console.log(`Context: ${context}`)
	console.log(`History: ${history}`)
	console.log(`Output: ${output}`)
	return output
}

async function callSelectRelevantSectionBackend(query, headings, context = "") {
	const response = await fetch(`${BACKEND_URL}/select-relevant-section`, {
		method: "post",
		headers: {
			"Content-type": "application/json",
		},
		body: JSON.stringify({
			options: Object.keys(headings),
			query: query,
			context: context,
			history: history
		}),
	})
	const responseJson = await response.json()
	const heading = responseJson["output"].replace(/\./g, "")

	const output = headings[heading]
		? { heading: heading, url: headings[heading] }
		: { heading: CURRENT_PAGE_HEADING, url: "" }

	console.log(`Query: ${query}`)
	console.log(`Headings: ${Object.keys(headings)}`)
	console.log(`Output: ${output.heading}`)
	return output
}

async function callTTSBackend(text) {
	console.log("Calling TTS...")
	const response = await fetch(`${BACKEND_URL}/text-to-speech`, {
		method: "post",
		headers: {
			"Content-type": "application/json",
		},
		body: JSON.stringify({
			text: text,
		}),
	})
	const responseJson = await response.json()
	const output = responseJson["output"]

	return output
}

async function callSTTBackend(audio) {
	console.log("Calling STT...")
	const formData = new FormData()
	formData.append("file", audio, "recording.wav")
	const response = await fetch(`${BACKEND_URL}/speech-to-text`, {
		method: "post",
		body: formData,
	})
	const responseJson = await response.json()
	const output = responseJson["output"]

	return output
}

async function speakSearchResult(){
	const textToSpeak = document.getElementById("search-result").innerHTML.split("<br>")[0]
	if (textToSpeak != "") {
		const ttsAudio = await callTTSBackend(textToSpeak)
		document.getElementById("audio-player").style.display = "block"
		document.getElementById(
			"audio-player"
		).src = `data:audio/mp3;base64,${ttsAudio}`
	}
}

function startRecording() {
	navigator.mediaDevices
		.getUserMedia({ audio: true })
		.then((stream) => {
			mediaRecorder = new MediaRecorder(stream)

			mediaRecorder.addEventListener("dataavailable", (event) => {
				chunks.push(event.data)
			})

			mediaRecorder.addEventListener("stop", async () => {
				const audioBlob = new Blob(chunks, { type: "audio/webm" })

				const arrayBuffer = await audioBlob.arrayBuffer()
				const audioContext = new AudioContext()
				const audioBuffer = await audioContext.decodeAudioData(
					arrayBuffer
				)
				const wavBuffer = toWav(audioBuffer)
				const wavBlob = new Blob([new DataView(wavBuffer)], {
					type: "audio/wav",
				})

				document.body.appendChild(
					Object.assign(document.createElement("a"), {
						href: URL.createObjectURL(wavBlob),
						download: "test.wav",
						innerHTML: "Click here to download",
					})
				)

				const transcription = await callSTTBackend(wavBlob)
				console.log(`Transcribed text: ${transcription}`)
				document.getElementById("user-query").value = transcription
				document.getElementById("search-button").click()

				chunks = []
				mediaRecorder = null
			})

			mediaRecorder.start()
		})
		.catch((error) => {
			console.error("Error accessing microphone:", error)
		})
}
