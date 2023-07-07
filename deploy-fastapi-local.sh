# .env must be in backend-fastapi/
pip install -qe backend-shared/
cd backend-fastapi/
pip install -qr requirements.txt
python server.py
