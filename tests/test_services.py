import pytest 
from app.models.models import Item
from app.services.services import filter_locations, search_by_keyword

items_list = [
    Item(id=0, name="calculator", location="office", sub_location="middle drawer", description="Sharp EL-W506", quantity=1),
    Item(id=0, name="laser level", location="office", sub_location="components cabinet drawer 3", description="Hychika", quantity=1),
    Item(id=1, name="resistors", location="office", sub_location="organisation_box-1.1A", description="multiple value resistors", quantity=100),
    Item(id=2, name="ESP32", location="office", sub_location="organisation_box-2.2J", description="microcontroller boards", quantity=5),
    Item(id=3, name="shovel", location="garage", sub_location="", description="garden shovel", quantity=1)
]

def test_filter_locations():
    result = filter_locations(location="garage", items_list=items_list)
    assert len(result) == 1
    assert type(result) == list
    assert result[0].location.lower() == "garage"

def test_search_by_keyword():
    result = search_by_keyword(keyword="drawer", items_list=items_list)
    assert len(result) == 2
    assert all(item.location.lower() == "office" for item in result)