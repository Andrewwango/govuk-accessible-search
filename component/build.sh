yarn webpack
cp src/index.html dist/index.html
cp src/index.css dist/index.css
cp src/index.css.map dist/index.css.map
python inject-inline-js.py dist/index.html