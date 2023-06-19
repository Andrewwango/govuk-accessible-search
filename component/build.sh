# Build JS (see webpack.config.js for details)
yarn webpack

# Copy HTMl + CSS
cp src/index.html dist/index.html
cp src/index.css dist/index.css
cp src/index.css.map dist/index.css.map

# Create NHS version of component
cp src/index.html dist/index_nhs.html
perl -pi -e 's/gov/nhs/g' dist/index_nhs.html

# Replace HTML script tags with inline JS
python inject-inline-js.py dist/index.html
python inject-inline-js.py dist/index_nhs.html