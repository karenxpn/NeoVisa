from fastapi import FastAPI
from fastapi.security import HTTPBearer

from auth.routes import router as auth_router
app = FastAPI()

security = HTTPBearer()

app.include_router(auth_router, prefix="/auth")


from user.routes import router as user_router
app.include_router(user_router)

