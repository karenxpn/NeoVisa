from fastapi import FastAPI

from auth.routes import router as auth_router
from user.routes import router as user_router
from order.routes import router as order_router
from visa_center.routes import router as vi_center_router
from payment.routes import router as payment_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(user_router)
app.include_router(vi_center_router)

app.include_router(order_router)
app.include_router(payment_router, prefix="/payment")