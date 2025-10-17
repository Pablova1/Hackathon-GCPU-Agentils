from fastapi import FastAPI
from app.api.profile_router import router as profile_router

app = FastAPI(title="Agentils Profiling API", version="1.0.0")

# On inclut ton router
app.include_router(profile_router)

@app.get("/")
def root():
    return {"message": "Agentils Profiling API fonctionne"}
