from pydantic import BaseModel, ConfigDict

class ProductCreate(BaseModel):
    name: str
    price: float
    in_stock: bool = True

class Product(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool = True

    model_config = ConfigDict(from_attributes=True)
    
class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    skip: int
    limit: int    
