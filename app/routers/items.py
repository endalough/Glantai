from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.routers import Item, ItemBase, ItemOptionals, all_attributes_none, SessionDep
from fastapi.templating import Jinja2Templates
import logging
from sqlmodel import select
from sqlalchemy.orm import Session

router_prefix = "/items"
router  = APIRouter(prefix=router_prefix)
logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory="app/templates")

@router.post("/create")
def create_item(session: SessionDep,
                name: str = Form(...),
                location: str = Form(...),
                sub_location: str = Form(...),
                description: str = Form(...),
                quantity: int = Form(...)
                ):
    item = Item(name=name, location=location, sub_location=sub_location, description=description, quantity=quantity)
    session.add(item)
    session.commit()
    session.refresh(item)
    return RedirectResponse(router_prefix, status_code=303)

@router.get("/")
def read_items(request: Request, session: SessionDep, page: int = 1, size: int = 5):
    offset = (page - 1) * size
    items = session.exec(select(Item).offset(offset).limit(size)).all()
    total_count = len(session.exec(select(Item)).all())

    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": items,
            "page": page,
            "total_pages": (total_count + size - 1) // size,
        },
    )

@router.patch("/{item_id}")
def update_item(item_id: int, item_optionals: ItemOptionals, session: SessionDep):
    item_db = session.get(Item, item_id)
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not in db") 
    item_dict = item_optionals.model_dump(exclude_unset=True)
    item_db.sqlmodel_update(item_dict)  
    session.add(item_db)
    session.commit()
    session.refresh(item_db)
    return RedirectResponse("/items", status_code=303)

@router.get("/{item_id}", response_model=Item)
def read_item_by_id(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        return HTTPException(status_code=404, detail="item not found in database")
    return item
    
@router.post("/delete/{item_id}")
def delete_item(item_id: int, session: SessionDep):
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found in db")
    session.delete(item)
    session.commit()
    return RedirectResponse(router_prefix, status_code=303)


@router.post("/name/{item_name}")
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


