from fastapi import APIRouter, HTTPException
from app.routers import Item, ItemBase, ItemOptionals, all_attributes_none, SessionDep
import logging
from sqlmodel import select

router  = APIRouter(prefix="/items")

logger = logging.getLogger(__name__)


@router.post("/", response_model=Item)
def create_item(item_base: ItemBase, session: SessionDep):
    item = Item.model_validate(item_base)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

@router.get("/", response_model=list[Item])
def read_items(session: SessionDep):
    items = session.exec(select(Item)).all()
    return items

@router.patch("/{item_id}", response_model=Item)
def update_item(item_id: int, item_optionals: ItemOptionals, session: SessionDep):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not in db") 
    item_dict = item_optionals.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_dict)  
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return item_db

    
@router.delete("/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in db")
    session.delete(item)
    session.commit()
    return {"ok": True}

@router.get("/{item_id}", response_model=Item)
def read_item_by_id(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        return HTTPException(status_code=404, detail="item not found in database")
    return item

@router.post("/name/{item_name}", response_model=list[Item])
def read_item_by_name(item_name: str, session: SessionDep):
    search_statement = select(Item).where(Item.name == item_name)
    item = session.exec(search_statement)
    if not item:
        return HTTPException(status_code=404, detail="item not found in database")
    return item

@router.post("/filtered/", response_model=list[Item])
def filter_items(item_optionals: ItemOptionals, session: SessionDep):
    logger.info("filtering")
    logger.info(item_optionals)
    if all_attributes_none(item_optionals):
        return "all values are none"
    
    items_to_search = item_optionals.model_dump(exclude_unset=True)
    query = select(Item)
    for key, value in items_to_search.items():
        logger.info(f"{key}: {value}")
        query = query.where(getattr(Item, key) == value)
        logger.info(query)
    items = session.exec(query).all()
    return items


