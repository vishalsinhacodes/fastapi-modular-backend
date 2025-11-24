import logging
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import ProductModel
from app.schemas.product import ProductCreate, Product, ProductListResponse

logger = logging.getLogger("app")

class ProductService:

    def create(self, db: Session, payload: ProductCreate) -> Product:
        product = ProductModel(**payload.model_dump())
        db.add(product)
        db.commit()
        db.refresh(product)
        
        logger.info(f"Product created: id={product.id}, name={product.name}")
        return Product.model_validate(product)

    def list(
        self, 
        db: Session,
        skip: int = 0,
        limit: int = 10,
        name: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        in_stock: bool | None = None,
    ) -> ProductListResponse:
        query = db.query(ProductModel)
        
        if name:
            # simple "contains" search
            query = query.filter(ProductModel.name.ilike(f"%{name}%"))
            
        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
            
        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
            
        if in_stock is not None:
            query = query.filter(ProductModel.in_stock == in_stock)
            
        total = query.count()
            
        query = query.order_by(ProductModel.id.desc())
        
        products = query.offset(skip).limit(limit).all()
        
        items = [Product.model_validate(p) for p in products]
        
        return ProductListResponse(items=items, total=total, skip=skip, limit=limit)
