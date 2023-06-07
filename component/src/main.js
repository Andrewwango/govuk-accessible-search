const htmlToText = require('html-to-text');

const BACKEND_URL = "https://shwast-fun-app.azurewebsites.net/api"
let scrapedText = ""

document.getElementById("search-button").addEventListener("click", async (event) => {
    let inputElement = document.getElementById("user-query")
    let outputElement = document.getElementById("search-result")

    try {
        outputElement.innerHTML = await handleSearch(inputElement.value)
    } catch(err) {
        console.log(err)
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
    let relevantPageRawHtml = ""

    const scrapedHeadings = scrapeHeadings(currentPageRawHtml) 
    const most_relevant_section = await callSelectRelevantSectionBackend(query, scrapedHeadings.map(x=>x.heading))
    
    if (most_relevant_section == "CURRENT PAGE") {
        relevantPageRawHtml = currentPageRawHtml
    } else {
        //TODO: logic to follow section's link and get that page's rawhtml
        relevantPageRawHtml = currentPageRawHtml
    }
    //TODO: flag to store heading for most recently cached text, if too much effort just remove caching
    scrapedText = (scrapedText == "") ? parseGovTextFromHtml(relevantPageRawHtml) : scrapedText
    const answer = await callQueryBackend(scrapedText, query)
    return answer
}

function scrapeHeadings(rawHtml) {
    const headings = htmlToText.convert(rawHtml, {
        wordwrap: false,
        baseElements: {
            selectors: [
                'nav.gem-c-contents-list', // GOV.UK "Contents" list
                'nav.beta-nhsuk-navigation-sideways', // NHS.UK child page "More in..." list
                'ul.nhsuk-hub-key-links'], // NHS.UK parent page "Contents" list
            returnDomByDefault: false
        }
    })
    //may need to look at "baseUrl" option for html-to-text to deal with scraped relative links
    const headingsList = headings
        .split('\n')
        .map((x) => x.split(/[*]|[0-9]+\.|[[]|[]]/) )
        .concat([['', 'CURRENT PAGE']])
        .map(x => {return {
            heading: x[1].trim(),
            url: x.length < 3 ? "" : x[2]
        }})

    console.log(headingsList)
    return headingsList
}

function parseGovTextFromHtml(rawHtml) {
    const prettyText = htmlToText.convert(rawHtml, {
        baseElements: {
            selectors: ['div.govuk-govspeak', 'article'],
            returnDomByDefault: false
        },
        selectors: [{
            selector: 'a',
            options: { ignoreHref: true }
        }]
    })
    return prettyText
}

async function callQueryBackend(context, query) {
    const response = await fetch(`${BACKEND_URL}/chatgpt`, {
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
    const response = await fetch(`${BACKEND_URL}/select-relevant-section`, {
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
