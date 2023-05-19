# gds-accessible-search
An intelligent search bar to improve accessibility on GOV.UK/NHS.UK pages using OpenAI. 

Kainos OpenAI submission for SHWAST (Beenita Shah, Oliver Stanley, Andrew Wang).

## Demo

GOV.UK websites can be downloaded using `wget`. Here is an example using the website describing [France foreign travel advice](https://www.gov.uk/foreign-travel-advice/france/entry-requirements):

```bash
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent --no-check-certificate https://www.gov.uk/foreign-travel-advice/france/entry-requirements
```

## Component

### Development

Note that the CSS file is only needed to import styles for the Government Design System components, and the assets (images and fonts) are those included with GDS following this [tutorial](https://frontend.design-system.service.gov.uk/get-started/#4-get-the-font-and-images-working). Therefore when integrating the component with a demo we probably wouldn't need to also copy across assets and the CSS. 

- Get started: `npm i yarn`, `yarn install`
- Run site locally: `yarn start`
- Recompile SASS: `yarn sass style.scss src/index.css`
