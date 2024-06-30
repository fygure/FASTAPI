# FASTAPI

## This project requires the following scripts to run locally:

### Docker Scripts
- `docker-compose build` to build the Docker images (only needed if there are changes to Dockerfile or dependencies)
- `docker-compose up` to start the application
- `docker-compose down` to stop running containers (Run this first when developing)
- `docker logs fastapi-otel-collector-1` will show the traces logged from the collector

### Virtual Environment Scripts
- `python -m venv venv` to create a venv
- `.\venv\Scripts\Activate` to activate venv
- `pip install -r requirements.txt` to install dependencies
- `pip freeze > requirements.txt` to capture current dependencies

### Local Development Scripts
- `uvicorn app:app --reload` to start the development server without Jaeger or OpenTelemetry

### These are the tools
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/latest/)
- [Uvicorn](https://www.uvicorn.org/)
- [Jaeger](https://www.jaegertracing.io/)
- [OpenTelemetry](https://opentelemetry.io/docs/languages/python/getting-started/)