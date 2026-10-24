from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import STAFF, require_roles
from ..models import InventoryItem, StockMovement, User
from ..schemas import AdjustIn, InventoryIn
from ..utils import log_action, to_dict

router = APIRouter(prefix="/inventory", tags=["inventory"])


def item_out(item: InventoryItem) -> dict:
    data = to_dict(item)
    data["is_low"] = item.quantity <= item.reorder_level
    return data


@router.get("")
def list_items(
    category: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*STAFF)),
):
    stmt = select(InventoryItem).order_by(InventoryItem.name)
    if category:
        stmt = stmt.where(InventoryItem.category == category)
    return [item_out(i) for i in db.scalars(stmt).all()]


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    items = db.scalars(select(InventoryItem).where(InventoryItem.quantity <= InventoryItem.reorder_level)).all()
    return [item_out(i) for i in items]


@router.post("", status_code=201)
def create_item(data: InventoryIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "nurse"))):
    item = InventoryItem(**data.model_dump())
    db.add(item)
    db.flush()
    if item.quantity:
        db.add(StockMovement(item_id=item.id, change=item.quantity, reason="Opening stock", user_id=user.id))
    db.commit()
    log_action(db, user.id, "create_item", item.name)
    return item_out(item)


@router.post("/{item_id}/adjust")
def adjust_stock(
    item_id: int, data: AdjustIn, db: Session = Depends(get_db), user: User = Depends(require_roles("admin", "nurse"))
):
    """Positive change = stock received, negative = used / wasted. Every change is recorded."""
    item = db.get(InventoryItem, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if item.quantity + data.change < 0:
        raise HTTPException(status_code=409, detail=f"Not enough stock (only {item.quantity} available)")
    item.quantity += data.change
    db.add(StockMovement(item_id=item.id, change=data.change, reason=data.reason, user_id=user.id))
    db.commit()
    log_action(db, user.id, "adjust_stock", f"{item.name}: {data.change:+d} ({data.reason})")
    return item_out(item)


@router.get("/{item_id}/movements")
def movements(item_id: int, db: Session = Depends(get_db), user: User = Depends(require_roles(*STAFF))):
    if db.get(InventoryItem, item_id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    rows = db.scalars(
        select(StockMovement).where(StockMovement.item_id == item_id).order_by(StockMovement.created_at.desc()).limit(100)
    ).all()
    return [to_dict(r) for r in rows]
