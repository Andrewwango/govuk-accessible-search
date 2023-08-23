# govuk-accessible-search
An intelligent search bar to improve accessibility on GOV.UK/NHS.UK pages using OpenAI. 

Kainos OpenAI submission for SHWAST (Beenita Shah, Oliver Stanley, Andrew Wang).

- [**GOV.UK demo**](https://andrewwango.github.io/govuk-accessible-search/demo/dist/www.gov.uk/foreign-travel-advice/france/entry-requirements.html)
- [**NHS.UK demo**](https://andrewwango.github.io/govuk-accessible-search/demo/dist/www.nhs.uk/conditions/covid-19/covid-19-vaccination/index.html)

**Note**: The current backend for the demo is deployed to Azure Functions on the free tier and as such is not always reliable - this could be mitigated by upgrading the plan in the future.

### Motivation

> The future of accessibility for government messaging

People for whom English is a foreign language (EFL) often need to read and understand important information and advice from GOV.UK and NHS websites, for example travel advice or public health advice. This includes those who may not even speak English at all.

These users need a quick and trustworthy way of naturally asking questions to a GOV.UK website in their own language.

These questions could be for example:
- _这个网站是关于什么的？_(What is this website about?)
- _Quel est le séjour maximum dans ce pays sans visa?_ (What is the maximum stay in this country without a visa?)

### Solution

We have built a tool that can answer natural-language questions on any government webpage. Our solution consists of 3 parts:

1. [Purely frontend component contained in one file](https://andrewwango.github.io/govuk-accessible-search/component/dist/index.html) which performs all the logic client-side.
2. We use a micro-backend to route API calls to an OpenAI API securely, without exposing our OpenAI API key to the frontend. This is deployed serverlessly.
3. Demo of a government website with the component inserted using Nunjucks, deployed statically to Github Pages

Our solution will provide the following functionality:

- Drop-in: insert the component into any webpage with only one HTML tag; the component is one file to be saved on server
- Lightweight: all processing is done client-side and the backend contains no program logic
- Multilingual: ask a question and receive an answer in any language, using ChatGPT's multilingual capabilities

## 1. Live demo

You can view a demo of the component in action on a sample government website here:
- Sample GOV.UK website [**demo**](https://andrewwango.github.io/govuk-accessible-search/demo/dist/www.gov.uk/foreign-travel-advice/france/entry-requirements.html)
- Sample NHS.UK website [**demo**](https://andrewwango.github.io/govuk-accessible-search/demo/dist/www.nhs.uk/conditions/covid-19/covid-19-symptoms-and-what-to-do/index.html)

If you get an error, make sure the backend is deployed and running, and the correct endpoint URL is referenced from the frontend.

## 2. Usage

To use our component on your government webpage, simply [build the component locally](#31-build-component-locally), copy the component HTML file from `component/dist/index.html` and insert the component using a Nunjucks `include`:

<!-- {% raw %} -->
```html
{% include "component/index.html" %}
```
<!-- {% endraw %} -->

at the desired location. Then build your website how you normally would. This embeds the component HTML along with all javascripts. CSS is not needed as the GOV.UK website will already have the necessary CSS.

## 3. Developer guide

### 3.1 Build component locally

Note that the CSS file is only needed to import styles for the Government Design System components, and the assets (images and fonts) are those included with GDS following this [tutorial](https://frontend.design-system.service.gov.uk/get-started/#4-get-the-font-and-images-working).

- Get started locally: `cd component`, `npm i yarn`, `yarn install`, `pip install beautifulsoup4` (for build process only)
- Build: `yarn build`
- Run site locally: `yarn test` (uses `live-server`)

This uses a custom build process in `component/build.sh`. First the Javascript, along with its dependencies, is bundled into a single script using `webpack`. Then HTML (and CSS) are copied across. Finally, all Javascripts are copied into the HTML as inline scripts (very hacky), allowing the component to be embedded in one line. You shouldn't ever have to touch the CSS as any GOV.UK website will already have the necessary CSS; however, if needed, recompile SASS with `yarn sass style.scss src/index.css`.

### 3.2 Build demo locally

- Get started locally: `cd demo`, `npm i yarn`, `yarn install`
- Build: `yarn build`
- Run site locally: `yarn test`

### 3.3 Add component to a new demo

1. Download a GOV.UK website. Here's an example using the website describing [France foreign travel advice](https://www.gov.uk/foreign-travel-advice/france/entry-requirements):

```bash
cd demo && wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --no-check-certificate https://www.gov.uk/foreign-travel-advice/france
```

2. [Build the component locally](#31-build-component-locally), and then add component anywhere in the website HTML using a Nunjucks include: 

<!-- {% raw %} -->
```html
{% include "component/index.html" %}
```
<!-- {% endraw %} -->

3. [Build your demo site locally](#32-build-demo-locally) and view it in your browser. Alternatively, build your Nunjucks site how you normally would.

Note: to use on a NHS webpage, instead include `component/index_nhs.html` which has all GOV.UK tags replaced with their NHS.UK counterparts.

### 3.4 Deploy demo

The component and demo frontends in this repo are configured to be remotely built and deployed to GitHub Pages for free. The build/deploy pipeline runs on a push to main. The remote build process simply follows the build instructions in Sections [3.1](#31-build-component-locally) and [3.2](#32-build-demo-locally).

### 3.5 Deploy backend

After deploying the backend, make sure to put the endpoint URL in the component source `component/src/main.js` and push to main to redeploy.

#### 3.5.1 To Deploy Locally as an Azure Function

Create `local.settings.json` based on the provided `local.settings.json.example` in `backend/`. Then ensure you have a Python virtual environment with all requirements activated. This can be set up as follows:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend-functions/requirements.txt
```

Then run the local deployment script.

```
bash deploy-local.sh
```

Once finishes, the created `temp/` directory can be safely deleted.

#### 3.5.2 To Deploy to Azure Functions

```
bash deploy-functions.sh
```

(if using a different function app, set `FUNCTION_APP` variable with the new name)

#### 3.5.3 To Deploy to Azure Container Instance

```
bash deploy-container.sh
```

You must also ensure `shwast-fun-app` resource is configured with the environment variables required (see `local.settings.json.example`).

### 3.6 Test backend

Use the text client.

```
cd text-client
pip install -r requirements.txt
python main.py
```
