from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from starlette.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional

from .utils import find_item
from .middleware import authenticate
from .database import DBItem, SessionLocal
import os

fastapi = FastAPI()

# inventory = [
#   {
#     "id": 1,
#     "name": "Treasure",
#     "quantity": 3
#   }
# ]


class Item(BaseModel):
  name: str
  quantity: int

class ItemUpdate(BaseModel):
  name: Optional[str] = Field(None, description="Optional name of the item")
  quantity: Optional[int] = Field(None, description="Optional quantity of the item")


# Routes
@fastapi.post("/items")
def create_item(item: Item, authenticated: bool = Depends(authenticate)):
    db = SessionLocal()
    new_item = DBItem(name=item.name, quantity=item.quantity)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {"item" :new_item}

@fastapi.get("/items")
async def get_items():
  db = SessionLocal()
  items = db.query(DBItem).all()
  return { "items": items }


@fastapi.get("/items/{item_id}")
def get_item(item_id: int):
    db = SessionLocal()
    item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item": item}

@fastapi.patch("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, authenticated: bool = Depends(authenticate)):
    db = SessionLocal()
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db_item.name = item.name
    db_item.quantity = item.quantity
    db.commit()
    db.refresh(db_item)
    return { "item": db_item}

@fastapi.delete("/items/{item_id}")
def delete_item(item_id: int, authenticated: bool = Depends(authenticate)):
    db = SessionLocal()
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}
  
@fastapi.patch("/item-image/{item_id}")
async def upload_file(item_id: int, file: UploadFile = File()):
    db = SessionLocal()
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
      
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    db_item.image_src = file.filename
    db.commit()
    db.refresh(db_item)
    
    return {"item": db_item}
  
@fastapi.get("/static/{file}")
async def serve_file(file: str):
    return FileResponse(os.path.join("uploads", file))

# @fastapi.get("/items") 
# async def get_items():
#   return {"items": inventory}


# @fastapi.get("/items/{item_id}")
# async def get_item(item_id: int):
#   item, idx = find_item(inventory, lambda x: x["id"] == item_id)
#   return { "item": item }

# @fastapi.delete("/items/{item_id}")
# async def delete_item(item_id: int, authenticated: bool = Depends(authenticate)):
#   item, idx = find_item(inventory, lambda x: x["id"] == item_id)
#   if idx == -1: return HTTPException(404, "item not found")
#   inventory.pop(idx)
#   return { "item": item }


# @fastapi.post("/items")
# async def add_item(data: Item, authenticated: bool = Depends(authenticate)):
#   item = {
#     "name": data.name,
#     "id": len(inventory) + 1,
#     "quantity": data.quantity
#   }
#   inventory.append(item)
#   return item

# @fastapi.patch("/items/{item_id}")
# async def update_item(item_id: int, item_update: ItemUpdate):
#   item, idx = find_item(inventory, lambda x: x["id"] == item_id)
#   if idx == -1:
#     raise HTTPException(status_code=404, detail="Item not found")

#   if item_update.name is not None:
#     item["name"] = item_update.name

#   if item_update.quantity is not None:
#     item["quantity"] = item_update.quantity

#   inventory[idx] = item

#   return item

