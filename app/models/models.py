from sqlmodel import Field, SQLModel

class ItemBase(SQLModel):
    name: str | None = Field(default=None, index=True)
    location: str | None = Field(default=None, index=True)
    sub_location: str | None =None
    description: str | None = None
    quantity: int | None = None
    
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ItemOptionals(ItemBase):
    name: str | None = None
    location: str | None = None
    sub_location: str | None = None
    description: str | None = None
    quantity: int | None = None

# class Location(SQLModel, table=True):
#     pass

def all_attributes_none(model: SQLModel) -> bool:
    return all(value is None for value in model.model_dump(exclude_unset=True).values())