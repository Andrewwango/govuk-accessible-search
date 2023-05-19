# Usage: python inject-inline-js.py file.html
import sys, os
from bs4 import BeautifulSoup

if len(sys.argv) != 2:
    raise ValueError("Filename not passed")

def inject_inline_js(filename):
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    script_tags = soup.find_all('script', src=True)

    for script_tag in script_tags:
        
        script_filename = os.path.join(os.path.dirname(filename), script_tag['src'])

        with open(script_filename, 'r') as js:
            new_tag = soup.new_tag('script')
            new_tag.string = js.read()
        
        script_tag.replace_with(new_tag)

    with open(filename, 'w') as f:
        f.write(str(soup))

if __name__ == "__main__":
    inject_inline_js(sys.argv[1])