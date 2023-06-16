// Imports
const htmlToText = require("html-to-text")

// Constants
const BACKEND_URL = "https://shwast-fun-app.azurewebsites.net/api"
const FIND_MOST_RELEVANT_SECTION = true
const CURRENT_PAGE_HEADING = "CURRENT PAGE"

// Global variables
let scrapedText = ""

document
	.getElementById("search-button")
	.addEventListener("click", async (event) => {
		let inputElement = document.getElementById("user-query")
		let outputElement = document.getElementById("search-result")
		if (inputElement.value == "") {
			return
		}
		try {
			outputElement.innerHTML = await handleSearch(inputElement.value)
		} catch (err) {
			console.log(err)
			outputElement.innerHTML =
				"Unknown error occured. Please try again later."
		}

		document.getElementById("search-result").style.display = "block"
	})

document
	.getElementById("user-query")
	.addEventListener("keypress", async (event) => {
		if (event.key === "Enter") {
			event.preventDefault()
			document.getElementById("search-button").click()
		}
	})

async function handleSearch(query) {
	let relevantPageRawHtml = getCurrentPageRawHtml()

	const scrapedHeadings = scrapeHeadings(relevantPageRawHtml)

	const mostRelevantHeading = FIND_MOST_RELEVANT_SECTION
		? await callSelectRelevantSectionBackend(query, scrapedHeadings)
		: {heading: CURRENT_PAGE_HEADING, url: ""}

    // Issue #17: persist the below to save time in a session
	if (mostRelevantHeading.url != "") {
		relevantPageRawHtml = await getExternalPageRawHtml(
			mostRelevantHeading.url
		)
	}

	scrapedText = parseGovTextFromHtml(relevantPageRawHtml)

	const answer = await callQueryBackend(scrapedText, query)

	const result = formatSearchResult(answer, mostRelevantHeading)

	return result
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
		.map((x) => {
			return {
				heading: x[1].trim(),
				url: x.length < 3 ? "" : x[2].replace(/[\[\]]/g, ""),
			}
		})

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
	const citation = (relevantHeading.heading == CURRENT_PAGE_HEADING) ? "the current page" : `<a href="${relevantHeading.url}" target="_blank">${relevantHeading.heading}</a>`
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
		}),
	})

	const responseJson = await response.json()
	const output = responseJson["output"]
	console.log(`Query: ${query}`)
	console.log(`Context: ${context}`)
	console.log(`Output: ${output}`)
	return output
}

async function callSelectRelevantSectionBackend(query, headings) {
	const response = await fetch(`${BACKEND_URL}/select-relevant-section`, {
		method: "post",
		headers: {
			"Content-type": "application/json",
		},
		body: JSON.stringify({
			options: headings.map((x) => x.heading),
			query: query,
		}),
	})
	const responseJson = await response.json()
	const output = responseJson["output"].replace(/\./g, "")

	let outputObject = headings.find(function (item) {
		return item.heading === output
	})
	outputObject = outputObject ? outputObject: {heading: CURRENT_PAGE_HEADING, url: ""}

	console.log(`Query: ${query}`)
	console.log(`Headings: ${headings.map((x) => x.heading)}`)
	console.log(`Output: ${outputObject.heading}`)
	return outputObject
}
