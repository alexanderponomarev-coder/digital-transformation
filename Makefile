.PHONY: api web test install smoke build docker-up docker-down native-install native-run

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

build:
	cd frontend && npm run build

smoke:
	bash scripts/smoke-deploy.sh http://127.0.0.1:8000

native-install:
	sudo bash deploy/debian/install.sh "$(CURDIR)"

native-run:
	sudo bash deploy/debian/run-native.sh 8080

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
