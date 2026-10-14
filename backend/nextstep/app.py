from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from nextstep.config import Settings

def create_app() -> FastAPI:
    app = FastAPI(title='NextStep Scholarships')
    app.state.settings = Settings()
    @app.get('/api/health')
    def health() -> dict[str, str]:
        return {'status': 'ok'}
    @app.api_route('/api/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'], include_in_schema=False)
    def missing_api(path: str):
        from fastapi import HTTPException
        raise HTTPException(404, 'API route not found')
    dist = Path(__file__).resolve().parents[2] / 'frontend' / 'dist'
    if dist.is_dir():
        app.mount('/', StaticFiles(directory=dist, html=True), name='ui')
    return app

app = create_app()
