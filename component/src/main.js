const htmlToText = require('html-to-text');

const BACKEND_URL = "https://shwast-fun-app.azurewebsites.net/api"
let scrapedText = ""

document.getElementById("search-button").addEventListener("click", async (event) => {
    let inputElement = document.getElementById("user-query")
    let outputElement = document.getElementById("search-result")

    try {
        outputElement.innerHTML = await handleSearch(inputElement.value)
    } catch(err) {
        outputElement.innerHTML = "Unknown error occured. Please try again later."
    }
    
    document.getElementById("search-result").style.display = "block"
})

document.getElementById("user-query").addEventListener("keypress", async (event) => {
    if (event.key === "Enter") {
        event.preventDefault()
        document.getElementById("search-button").click()
    }
});

async function handleSearch(query) {
    const currentPageRawHtml = window.parent.document.body.outerHTML
    const scrapedHeadings = scrapeHeadings(currentPageRawHtml) 
    //const most_relevant_section = await callSelectRelevantSectionBackend(query, scrapedHeadings)
    const most_relevant_section = "CURRENT PAGE"
    
    if (most_relevant_section == "CURRENT PAGE") {
        const relevantPageRawHtml = currentPageRawHtml
    } else {
        //TODO: logic to follow section's link and get that page's rawhtml
        const relevantPageRawHtml = ""
    }
    //TODO: flag to store heading for most recently cached text, if too much effort just remove caching
    scrapedText = (scrapedText == "") ? parseGovTextFromHtml(relevantPageRawHtml) : scrapedText
    const answer = await callQueryBackend(scrapedText, query)
    return answer
}

function scrapeHeadings(rawHtml) {
    const headings = htmlToText.convert(rawHtml, {
        baseElements: {
            selectors: ['li.gem-c-contents-list__list-item']
        }
    })
    console.log(headings)
    return ""
}

function parseGovTextFromHtml(rawHtml) {
    const prettyText = htmlToText.convert(rawHtml, {
        baseElements: {
            selectors: ['div.govuk-govspeak', 'article']
        },
        selectors: [{
            selector: 'a',
            options: { ignoreHref: true }
        }]
    })
    return prettyText
}

async function callQueryBackend(context, query) {
    const response = await fetch(`${BACKEND_URL}/chatgpt}`, {
        method: 'post',
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify({
            "context": context,
            "query": query
        })
    })

    const responseJson = await response.json()
    const output = responseJson["output"]
    console.log(`Query: ${query}`)
    console.log(`Context: ${context}`)
    console.log(`Output: ${output}`)
    return output
}

async function callSelectRelevantSectionBackend(query, headings) {
    const response = await fetch(`${BACKEND_URL}/select-relevant-section}`, {
        method: 'post',
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify({
            "options": headings,
            "query": query
        })
    })
    const responseJson = await response.json()
    const output = responseJson["output"]
    console.log(`Query: ${query}`)
    console.log(`Headings: ${headings}`)
    console.log(`Output: ${output}`)
    return output
}
