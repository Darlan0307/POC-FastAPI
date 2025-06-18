from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from schemas import OrderSchema
from dependencies import (
    get_session, 
    get_current_user, 
    require_admin,
)
from models import Order, User
from logger import logger

order_router = APIRouter(prefix="/orders", tags=["orders"])

@order_router.get("/")
async def get_orders(
    request: Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    orders = session.query(Order).filter(Order.user == current_user.id).all()
    
    return {
        "message": "Seus pedidos",
        "total_orders": len(orders),
        "orders": [{"id": order.id, "user": order.user} for order in orders]
    }

@order_router.post("/")
async def create_order(
    order_schema: OrderSchema,
    session:Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    novo_pedido = Order(user=current_user.id)
    session.add(novo_pedido)
    session.commit()
    return {
        "message": f"Pedido criado com sucesso",
        "order_id": novo_pedido.id,
        "user": current_user.name
    }

@order_router.get("/admin/all")
async def get_all_orders(
    session: Session = Depends(get_session),
    admin_user: User = Depends(require_admin)
):
    orders = session.query(Order).all()
    
    logger.info(f"Admin {admin_user.email} listou todos os {len(orders)} pedidos")
    
    return {
        "message": "Todos os pedidos do sistema",
        "admin": admin_user.name,
        "total_orders": len(orders),
        "orders": [{"id": order.id, "user": order.user} for order in orders]
    }
