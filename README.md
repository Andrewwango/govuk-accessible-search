# gds-accessible-search
An intelligent search bar to improve accessibility on GOV.UK/NHS.UK pages using OpenAI. 

Kainos OpenAI submission for SHWAST (Beenita Shah, Oliver Stanley, Andrew Wang).

## Demo

A demo of the component in action on a sample GOV.UK website can be viewed here: https://andrewwango.github.io/gds-accessible-search/demo/www.gov.uk/foreign-travel-advice/france/entry-requirements.html

### Get started

GOV.UK websites can be downloaded using `wget`. Here is an example using the website describing [France foreign travel advice](https://www.gov.uk/foreign-travel-advice/france/entry-requirements):

```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --no-check-certificate https://www.gov.uk/foreign-travel-advice/france/entry-requirements
```

## Component

### Usage

To use the component on a demo page, simply add:

```html
<embed src="../../../../component/dist/index.html" height="300"></embed>
```

to any HTML page in the demo. Adjust the number of `../` as necessary.

This embeds the component HTML along with all javascripts. CSS is not needed as the GOV.UK website will already have the necessary CSS.

### Development

Note that the CSS file is only needed to import styles for the Government Design System components, and the assets (images and fonts) are those included with GDS following this [tutorial](https://frontend.design-system.service.gov.uk/get-started/#4-get-the-font-and-images-working).

- Get started locally: `npm i yarn`, `yarn install`, `pip install beautifulsoup4` (for build process only)
- Build: `yarn build` (see below)
- Run site locally: `yarn test` (using `live-server`)
- Recompile SASS: `yarn sass style.scss src/index.css`

#### Build
This uses a custom build process in `component/build.sh`. First the Javascript, along with its dependencies, is bundled into a single script using `webpack`. Then HTML (and CSS) are copied across. Finally, all Javascripts are copied into the HTML as inline scripts (very hacky), allowing the component to be embedded in one line.
## Demo

A demo of the component in action on a sample GOV.UK website can be viewed here: https://andrewwango.github.io/gds-accessible-search/demo/www.gov.uk/foreign-travel-advice/france/entry-requirements.html

### Get started

GOV.UK websites can be downloaded using `wget`. Here is an example using the website describing [France foreign travel advice](https://www.gov.uk/foreign-travel-advice/france/entry-requirements):

```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --no-check-certificate https://www.gov.uk/foreign-travel-advice/france/entry-requirements
```
