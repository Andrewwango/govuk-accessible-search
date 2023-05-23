const htmlToText = require('html-to-text');

document.getElementById("search-button").addEventListener("click", (event) => {
    let inputElement = document.getElementById("user-query")
    let outputElement = document.getElementById("search-result")
    document.getElementById("search-result").style.display = "block"
    outputElement.innerHTML = handleSearch(inputElement.value)
});

function handleSearch(query) {
    let documentText = scrapeCurrentPage()
    let prompt = constructPrompt(documentText, query)
    let response = callBackend(prompt) //may need to be asynchronous
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
            options: {ignoreHref: true}
        }]
    })
    return prettyText
}

function constructPrompt(context, query) {
    const prompt = 
    `Given the following information:

    ${context}

    ${query}?
    `
    return prompt
}

function callBackend(prompt) {
    console.log(prompt)
    return `See console for prompt to be sent to backend` 
}