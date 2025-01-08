# Business logic
from app.models.models import Item
from typing import get_args

# helper method to check union types
def check_union_type(union, target):
    args = get_args(union)
    return target in args

# method to filter all items based on column
def filter_locations(location: str, items_list: list[Item]) -> list[Item]:
    filtered_item_list = []
    for item in items_list:
        if item.location.lower() == location:
            filtered_item_list.append(item)
    return filtered_item_list

    


# method to search and return all items that contain a keyword
def search_by_keyword(keyword: str, items_list: list[Item]) -> list[Item]:
    keyword = keyword.lower()
    columns = [name for name, field in Item.model_fields.items()
               if check_union_type(field.annotation, str)]
    filtered_item_list = [item for item in items_list if any(keyword in getattr(item, column).lower() for column in columns)]
    return filtered_item_list


if __name__ == "__main__":
    print("Running")
    items = [Item(id=1, name="office chair", location="office", sub_location="by table",description="comfy chair", quantity=3),
             Item(id=1, name="walkman", location="bedroom", sub_location="bedside locker",description="music player", quantity=1),
             Item(id=1, name="monitor", location="bedroom", sub_location="cupboard",description="could be useful in office", quantity=1)
             ]
    print(search_by_keyword("office", items))

