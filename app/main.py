from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI

from app.routers import analysis, auth, instituicoes
from app.settings import Settings

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(settings.MODEL_PATH)
    app.state.scaler = joblib.load(settings.SCALER_PATH)
    yield
    del app.state.model
    del app.state.scaler


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
