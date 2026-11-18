.PHONY: api web test install

install:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r backend/requirements.txt
	cd frontend && npm install

api:
	. .venv/bin/activate && cd backend && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

web:
	cd frontend && npm run dev -- --host 127.0.0.1 --port 5173

test:
	. .venv/bin/activate && cd backend && pytest -q
