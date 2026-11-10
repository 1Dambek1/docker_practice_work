from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Orders API")


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price_kopecks: int = Field(gt=0)


class Product(ProductCreate):
    id: int


class OrderCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class Order(OrderCreate):
    id: int


products: dict[int, Product] = {}
orders: list[Order] = []


@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate) -> Product:
    product = Product(id=len(products) + 1, **data.model_dump())
    products[product.id] = product
    return product


@app.get("/products")
async def list_products() -> list[Product]:
    return list(products.values())


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate) -> Order:
    if data.product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    order = Order(id=len(orders) + 1, **data.model_dump())
    orders.append(order)
    return order


@app.get("/orders")
async def list_orders() -> list[Order]:
    return orders
