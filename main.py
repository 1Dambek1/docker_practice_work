from pathlib import Path

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Утренняя смена")
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=200)
    price_kopecks: int = Field(gt=0)
    stock: int = Field(default=10, ge=0)


class Product(ProductCreate):
    id: int


class OrderCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class Order(OrderCreate):
    id: int
    total_kopecks: int


products = {
    1: Product(id=1, name="Фильтр", description="Чёрный кофе с нотами вишни.", price_kopecks=19000, stock=6),
    2: Product(id=2, name="Ванильный раф", description="Эспрессо, сливки и ваниль.", price_kopecks=29000, stock=4),
    3: Product(id=3, name="Булочка с корицей", description="Из первой партии в духовке.", price_kopecks=22000, stock=2),
}
orders: list[Order] = []


@app.get("/", include_in_schema=False)
async def storefront() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate) -> Product:
    product = Product(id=len(products) + 1, **data.model_dump())
    products[product.id] = product
    return product


@app.get("/products")
async def list_products(response: Response) -> list[Product]:
    response.headers["X-Cache"] = "BYPASS"
    return list(products.values())


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate) -> Order:
    product = products.get(data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if data.quantity > product.stock:
        raise HTTPException(status_code=409, detail="Not enough stock")

    order = Order(
        id=len(orders) + 1,
        total_kopecks=product.price_kopecks * data.quantity,
        **data.model_dump(),
    )
    product.stock -= data.quantity
    orders.append(order)
    return order


@app.get("/orders")
async def list_orders() -> list[Order]:
    return orders
