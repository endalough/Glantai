from fastapi import APIRouter, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from app.models.models import Item, ItemBase, ItemOptionals, all_attributes_none
from app.core.database import SessionDep
from app.services.services import search_by_keyword, filter_locations
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

@router.get("/locations")
def get_all_locations(session: SessionDep):
    unique_locations = session.exec(select(Item.location).distinct()).all()
    return unique_locations

@router.get("/")
def read_items(request: Request, session: SessionDep, page: int = 1, size: int = 5):
    offset = (page - 1) * size
    logger.debug(f"page: {page}")
    logger.debug(f"offset: {offset}")
    items = session.exec(select(Item).offset(offset).limit(size)).all()
    total_count = len(session.exec(select(Item)).all())
    # locations = session.exec(select(Item.location).distinct()).all()
    locations = get_all_locations(session=session)

    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": items,
            "page": page,
            "total_pages": (total_count + size - 1) // size,
            "locations": locations
        },
    )
@router.get("/search")
def search(request: Request, session: SessionDep, query: str = Query(...), page: int = 1, size: int = 5):
    logger.info(f"query: {query}")

    offset = (page - 1) * size
    logger.debug(f"page: {page}")
    logger.debug(f"offset: {offset}")

    items = session.exec(select(Item)).all()
    filtered_items = search_by_keyword(query, items)

    end_index = offset + size
    filtered_items_length = len(filtered_items)
    logging.debug(f"filtered_items_length: {len(filtered_items)}")

    if end_index > filtered_items_length:
        logger.debug("if")
        paginated_items = filtered_items[offset:]
        logger.debug(f"start: {filtered_items[offset-1].id}")
    else:
        logger.debug("else")
        paginated_items = filtered_items[offset: offset + size]

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "items": paginated_items,
            "page": page,
            "total_pages": (filtered_items_length + size - 1) // size,
            "query": query,
            "size": size
        },
    )

@router.get("/filtered")
def filter_items(request: Request, session: SessionDep, location: str = Query(...), page: int = 1, size: int = 5):
    location = location.lower()
    items = session.exec(select(Item)).all()
    offset = (page - 1) * size

    locations = get_all_locations(session=session) # this is to populate the dropdown


    filtered_items = filter_locations(location, items)

    end_index = offset + size
    filtered_items_length = len(filtered_items)
    logging.debug(f"filtered_items_length: {len(filtered_items)}")

    if end_index > filtered_items_length:
        logger.debug("if")
        paginated_items = filtered_items[offset:]
        logger.debug(f"start: {filtered_items[offset-1].id}")
    else:
        logger.debug("else")
        paginated_items = filtered_items[offset: offset + size]

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "items": paginated_items,
            "page": page,
            "total_pages": (filtered_items_length + size - 1) // size,
            "query": location,
            "locations": locations,
            "size": size
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







