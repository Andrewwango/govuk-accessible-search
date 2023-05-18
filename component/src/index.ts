function searchButtonPressed() {

    let inputElement = document.getElementById("user-query") as HTMLInputElement;
    let outputElement = document.getElementById("search-result") as HTMLElement
    outputElement.innerHTML = handleSearch(inputElement.value)
}

function handleSearch(query: string): string {
    let documentText = scrapeCurrentPage()
    let prompt = constructPrompt(documentText, query)
    let response = callBackend(prompt) //may need to be asynchronous

    return response
}

function scrapeCurrentPage(): string {
    // Scrape
    // Parse
    return ""
}

function constructPrompt(context: string, query: string) {
    return query
}

function callBackend(prompt: string): string {
    return "Your query was: " + prompt
}