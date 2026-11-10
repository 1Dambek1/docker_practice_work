const catalog = document.querySelector("#catalog");
const template = document.querySelector("#product-card");
const cacheState = document.querySelector("#cache-state");
const catalogMessage = document.querySelector("#catalog-message");
const orderMessage = document.querySelector("#order-message");
const refreshButton = document.querySelector("#refresh");
const rubles = new Intl.NumberFormat("ru-RU", { style: "currency", currency: "RUB" });

function renderProducts(products) {
  catalog.replaceChildren();
  for (const product of products) {
    const card = template.content.cloneNode(true);
    card.querySelector("h3").textContent = product.name;
    card.querySelector(".description").textContent = product.description;
    card.querySelector(".price").textContent = rubles.format(product.price_kopecks / 100);
    card.querySelector(".stock").textContent = product.stock ? `Остаток: ${product.stock}` : "Разобрали";

    const button = card.querySelector("button");
    button.disabled = product.stock === 0;
    button.setAttribute("aria-label", `Заказать: ${product.name}`);
    button.addEventListener("click", () => runAction(() => placeOrder(product.id)));
    catalog.append(card);
  }
}

async function refreshCatalog() {
  try {
    const response = await fetch("/products", { cache: "no-store" });
    if (!response.ok) throw new Error("Catalog request failed");

    const products = await response.json();
    cacheState.textContent = `Кэш: ${response.headers.get("X-Cache") ?? "—"}`;
    catalogMessage.textContent = products.length ? "" : "Меню пока пустое. Добавьте товар через документацию API.";
    renderProducts(products);
  } catch {
    cacheState.textContent = "Кэш: —";
    catalogMessage.textContent = "Не удалось обновить меню. Попробуйте ещё раз.";
  }
}

async function placeOrder(productId) {
  orderMessage.textContent = "";
  try {
    const response = await fetch("/orders", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });
    if (response.status === 409) {
      orderMessage.textContent = "Эту позицию уже разобрали.";
    } else {
      if (!response.ok) throw new Error("Order request failed");
      const order = await response.json();
      orderMessage.textContent = `Заказ №${order.id} принят · ${rubles.format(order.total_kopecks / 100)}`;
    }
    await refreshCatalog();
  } catch {
    orderMessage.textContent = "Не удалось подтвердить заказ.";
  }
}

async function runAction(action) {
  refreshButton.disabled = true;
  catalog.inert = true;
  try {
    await action();
  } finally {
    catalog.inert = false;
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", () => runAction(refreshCatalog));
runAction(refreshCatalog);
