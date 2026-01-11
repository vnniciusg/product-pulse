run-dev:
	uv run uvicorn src.server:app --reload --port 8000

run: 
	uv run uvicorn src.server:app --port 8000
