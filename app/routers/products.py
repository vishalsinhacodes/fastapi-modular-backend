import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, Product, ProductListResponse
from app.core.security import get_current_user, require_admin
from app.core.redis_client import get_json, set_json, delete_prefix
from app.models.user import UserModel
from app.models.product import ProductModel
from app.dependencies.rate_limit_dep import rate_limit_dependency

logger = logging.getLogger("app")

router = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()

@router.post("/", response_model=Product)
def create(
    payload: ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    product = service.create(db, payload)
    delete_prefix("products:")
    return product

@router.get("/", response_model=ProductListResponse, dependencies=[Depends(rate_limit_dependency)])
def list_products(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10,
    name: str | None = None,
    min_price: str | None = None,
    max_price: str | None = None,
    in_stock: bool | None = None,
):
    # Build a cache key based on query params
    key_parts = [
        f"skip={skip}",
        f"limit={limit}",
        f"name={name or ''}",
        f"min_price={min_price if min_price is not None else ''}",
        f"max_price={max_price if max_price is not None else ''}",
        f"in_stock={in_stock if in_stock is not None else ''}",
    ]
    cache_key = "products:" + "&".join(key_parts)
    
    # 1) Try cache first
    cached = get_json(cache_key)
    if cached is not None:
        logger.info(f"[CACHE HIT] {cache_key}")
        return ProductListResponse(**cached)
    
    logger.info(f"[CACHE MISS] {cache_key}")
    
    # 2) Cache miss → hit DB
    result = service.list(db,
        skip=skip,
        limit=limit,
        name=name,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
    )
    
    # 3) Store in cache (convert to dict for JSON)
    set_json(cache_key, result.model_dump(), ttl_seconds=60)
    
    return result
    
@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: UserModel = Depends(require_admin),
):
    product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if not product:
        from app.core.errors import NotFoundError
        raise NotFoundError("Product not found", code="PRODUCT_NOT_FOUND")
    
    db.delete(product)
    db.commit()
    
    delete_prefix("products:")
    return
