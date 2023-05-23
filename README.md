# gds-accessible-search
An intelligent search bar to improve accessibility on GOV.UK/NHS.UK pages using OpenAI. 

Kainos OpenAI submission for SHWAST (Beenita Shah, Oliver Stanley, Andrew Wang).

### Motivation

> The future of accessibility for goverment messaging

People for whom English is a foreign language (EFL) often need to read and understand important information and advice from GOV.UK and NHS websites, for example travel advice or public health advice. This includes those who may not even speak English at all.

These users need a quick and trustworthy way of naturally asking questions to a GOV.UK website in their own language.

These questions could be for example:
- _这个网站是关于什么的？_(What is this website about?)
- _Quel est le séjour maximum dans ce pays sans visa?_ (What is the maximum stay in this country without a visa?)

### Solution

We have built a tool that can answer natural-language questions on any government webpage. Our solution consists of 3 parts:

1. [Frontend component contained in one file](https://andrewwango.github.io/gds-accessible-search/component/dist/index.html) which performs all the logic client-side.
2. A very simple backend to call the OpenAI API. This is deployed serverlessly
3. Demo of a government website with the component embedded using one line of HTML, deployed statically to Github Pages

Our solution will provide the following functionality:

- Drop-in: insert the component into any webpage with only one HTML tag; the component is one file to be saved on server
- Lightweight: all processing is done client-side and the backend contains no program logic
- Multilingual: ask a question and receive an answer in any language, using ChatGPT's multilingual capabilities

## Demo

A demo of the component in action on a sample GOV.UK website can be viewed [live here](https://andrewwango.github.io/gds-accessible-search/demo/www.gov.uk/foreign-travel-advice/france/entry-requirements.html).

### Get started

GOV.UK websites can be downloaded using `wget`. Here is an example using the website describing [France foreign travel advice](https://www.gov.uk/foreign-travel-advice/france/entry-requirements):

```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --no-check-certificate https://www.gov.uk/foreign-travel-advice/france/entry-requirements
```

## Component

### Usage

To use the component on a demo page, simply add:

```html
<embed src="https://andrewwango.github.io/gds-accessible-search/component/dist/index.html" height="300"></embed>
```

to any HTML page in the demo. This embeds the component HTML along with all javascripts. CSS is not needed as the GOV.UK website will already have the necessary CSS.

To run a demo page locally, you will need to add the component locally (due to [same-origin policy](https://stackoverflow.com/a/25098153)): 

<embed src="../../../../component/dist/index.html" height="300"></embed>

And adjust the number of `../` as necessary. Use `live-server` to spin up a web server:

```bash
cd component && yarn live-server ..
```

### Development

Note that the CSS file is only needed to import styles for the Government Design System components, and the assets (images and fonts) are those included with GDS following this [tutorial](https://frontend.design-system.service.gov.uk/get-started/#4-get-the-font-and-images-working).

- Get started locally: `npm i yarn`, `yarn install`, `pip install beautifulsoup4` (for build process only)
- Build: `yarn build` (see below)
- Run site locally: `yarn test` (using `live-server`)
- Recompile SASS (only if needed): `yarn sass style.scss src/index.css`

#### Build
This uses a custom build process in `component/build.sh`. First the Javascript, along with its dependencies, is bundled into a single script using `webpack`. Then HTML (and CSS) are copied across. Finally, all Javascripts are copied into the HTML as inline scripts (very hacky), allowing the component to be embedded in one line.

## Backend

The backend only exists to call the OpenAI API, and therefore is very lightweight and can be easily modified to call a different chat API. 

### Get started locally

### Deployment