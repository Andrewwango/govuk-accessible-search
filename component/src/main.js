const htmlToText = require('html-to-text');

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
    scrapedText = (scrapedText == "") ? scrapeCurrentPage() : scrapedText
    const response = await callBackend(scrapedText, query)
    return response
}

function scrapeCurrentPage() {
    const rawHtml = window.parent.document.body.outerHTML
    const prettyText = htmlToText.convert(rawHtml, {
        baseElements: {
            selectors: ['div.govuk-govspeak']
        },
        selectors: [{
            selector: 'a',
            options: { ignoreHref: true }
        }]
    })
    return prettyText
}

async function callBackend(context, query) {
    BACKEND_URL = "https://shwast-fun-app.azurewebsites.net/api/chatgpt"

    const response = await fetch(BACKEND_URL, {
        method: 'post',
        headers: {
            "Content-type": "application/json"
        },
        body: JSON.stringify({
            "context": context,
            "query": query
        })
    });

    const responseJson = await response.json();
    const output = responseJson["output"]
    console.log(`Prompt: ${prompt}`)
    console.log(`Output: ${output}`)
    return output
}
