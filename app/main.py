from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI

from app.routers import analysis, auth, instituicoes
from app.settings import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: carrega o modelo uma vez e guarda no estado da app
    app.state.model = joblib.load(settings.MODEL_PATH)
    yield
    # Shutdown: limpa o modelo da memória
    del app.state.model


app = FastAPI(
    title='FraudZero API',
    description='API de detecção de fraudes bancárias com Machine Learning.',
    version='0.1.0',
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(instituicoes.router)
app.include_router(analysis.router)


@app.get('/', tags=['health'])
def read_root():
    return {'status': 'online', 'message': 'FraudZero API está no ar.'}
