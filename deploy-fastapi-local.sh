rm -r temp/
cp -r backend-fastapi/ temp/
cp -r backend-shared/ temp/
cd temp/
python server.py
