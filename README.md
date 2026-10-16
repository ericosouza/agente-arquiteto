# ---------- Backend ----------
cd C:\Users\erico\OneDrive\Documentos\DEV\agente-arquiteto\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env   # opcional
uvicorn app.main:app --reload --port 8000

# ---------- Frontend ----------
cd C:\Users\erico\OneDrive\Documentos\DEV\agente-arquiteto\frontend
npm install
npm run dev          # dev server
# ou
npm run build        # produção (servida pelo FastAPI)
