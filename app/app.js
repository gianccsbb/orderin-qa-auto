/* Quebra-Mar pickup ordering — STAGING v0.9 (system under test).
 *
 * This build intentionally contains four defects ("seeded bugs") so the test
 * suite and bug reports have something real to find. Each one is marked with
 * "SEEDED BUG" and documented in docs/bug-reports.md.
 */
(() => {
  const PRODUCTS = [
    { id: "coado", name: "Café coado", cat: "cafes", price: 600, featured: 1 },
    { id: "cappuccino", name: "Cappuccino", cat: "cafes", price: 1200, featured: 2 },
    { id: "gelado", name: "Café gelado com rapadura", cat: "cafes", price: 1400, featured: 5 },
    { id: "chapa", name: "Pão na chapa", cat: "padaria", price: 700, featured: 3 },
    { id: "tapioca", name: "Tapioca de queijo coalho", cat: "padaria", price: 1400, featured: 6 },
    { id: "croissant", name: "Croissant", cat: "padaria", price: 1100, featured: 8 },
    { id: "rolo", name: "Bolo de rolo (fatia)", cat: "doces", price: 1000, featured: 4 },
    { id: "brigadeiro", name: "Brigadeiro", cat: "doces", price: 400, featured: 7 },
  ];
  const COUPONS = { BOAVIAGEM10: 0.10 };
  const OPEN = "07:00", CLOSE = "19:00";

  const $ = (s) => document.querySelector(`[data-testid="${s}"]`);
  const brl = (c) => (c / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" }).replace(/ /g, " ");
  const state = { cart: new Map(), discountRate: 0 };

  function renderProducts() {
    const cat = $("category-filter").value;
    const sort = $("sort").value;
    let list = PRODUCTS.filter((p) => cat === "all" || p.cat === cat);
    if (sort === "name") list = [...list].sort((a, b) => a.name.localeCompare(b.name, "pt-BR"));
    else if (sort === "price-asc") {
      // SEEDED BUG-001: sorts by the formatted price text instead of the number,
      // so "R$ 11,00" comes before "R$ 4,00".
      list = [...list].sort((a, b) => brl(a.price).localeCompare(brl(b.price)));
    } else list = [...list].sort((a, b) => a.featured - b.featured);

    const ul = $("product-list");
    ul.innerHTML = "";
    for (const p of list) {
      const li = document.createElement("li");
      li.className = "product";
      li.setAttribute("data-testid", "product");
      li.dataset.id = p.id;
      li.innerHTML = `<span class="name" data-testid="product-name"></span>
        <span class="price" data-testid="product-price">${brl(p.price)}</span>
        <span class="cat">${{ cafes: "Cafés", padaria: "Padaria", doces: "Doces" }[p.cat]}</span>
        <button type="button" data-testid="add-to-cart">Adicionar</button>`;
      li.querySelector(".name").textContent = p.name;
      li.querySelector("button").setAttribute("aria-label", `Adicionar ${p.name}`);
      ul.append(li);
    }
  }

  function subtotal() {
    let s = 0;
    for (const [id, qty] of state.cart) s += PRODUCTS.find((p) => p.id === id).price * qty;
    return s;
  }

  function updateTotals() {
    const sub = subtotal();
    const disc = Math.round(sub * state.discountRate);
    $("subtotal").textContent = brl(sub);
    $("discount").textContent = disc ? "− " + brl(disc) : brl(0);
    $("total").textContent = brl(sub - disc);
    let count = 0;
    for (const q of state.cart.values()) count += q;
    $("cart-count").textContent = String(count);
    $("checkout-button").disabled = state.cart.size === 0;
    $("cart-empty").hidden = state.cart.size !== 0;
  }

  function renderCart() {
    const ul = $("cart-items");
    ul.innerHTML = "";
    for (const [id, qty] of state.cart) {
      const p = PRODUCTS.find((x) => x.id === id);
      const li = document.createElement("li");
      li.className = "cart-item";
      li.setAttribute("data-testid", "cart-item");
      li.dataset.id = id;
      li.innerHTML = `<span data-testid="cart-item-name"></span>
        <input type="number" min="1" max="20" value="${qty}" data-testid="qty-input">
        <button type="button" class="remove" data-testid="remove-item">Remover</button>`;
      li.querySelector("span").textContent = p.name;
      li.querySelector("input").setAttribute("aria-label", `Quantidade de ${p.name}`);
      li.querySelector("button").setAttribute("aria-label", `Remover ${p.name}`);
      ul.append(li);
    }
  }

  function addToCart(id) {
    state.cart.set(id, Math.min((state.cart.get(id) || 0) + 1, 20));
    renderCart();
    updateTotals();
  }

  function removeFromCart(id) {
    state.cart.delete(id);
    renderCart();
    // SEEDED BUG-004: totals are not recalculated after removing an item,
    // so subtotal, total and the cart badge keep showing the old values.
    $("checkout-button").disabled = state.cart.size === 0;
    $("cart-empty").hidden = state.cart.size !== 0;
  }

  function applyCoupon(code) {
    const msg = $("coupon-msg");
    const rate = COUPONS[code.trim().toUpperCase()];
    if (!rate) {
      msg.textContent = "Cupom inválido.";
      msg.className = "msg bad";
      return;
    }
    // SEEDED BUG-002: no check for an already-applied coupon, so every click
    // adds another 10% off (10%, 20%, 30%...).
    state.discountRate += rate;
    msg.textContent = `Cupom aplicado: ${Math.round(rate * 100)}% de desconto.`;
    msg.className = "msg ok";
    updateTotals();
  }

  function validatePhone(raw) {
    // SEEDED BUG-003: only the length is checked, so letters and symbols pass
    // (e.g. "abcdefghijk"). It should require 10 or 11 digits.
    return raw.replace(/\s/g, "").length >= 10;
  }

  function validate() {
    let ok = true;
    const name = $("name-input").value.trim();
    const phone = $("phone-input").value;
    const pickup = $("pickup-input").value;
    $("name-error").textContent = name.length >= 2 ? "" : "Informe seu nome.";
    $("phone-error").textContent = validatePhone(phone) ? "" : "Telefone inválido.";
    if (!pickup) $("pickup-error").textContent = "Escolha um horário.";
    else if (pickup < OPEN || pickup >= CLOSE) $("pickup-error").textContent = "Escolha um horário entre 7h e 19h.";
    else $("pickup-error").textContent = "";
    for (const id of ["name-error", "phone-error", "pickup-error"]) if ($(id).textContent) ok = false;
    return ok;
  }

  function placeOrder() {
    const total = $("total").textContent;
    const number = "QM-" + String(1000 + Math.floor(Math.random() * 9000));
    $("checkout-dialog").close();
    document.querySelector("main").hidden = true;
    $("order-number").textContent = number;
    $("order-total").textContent = total;
    $("order-pickup").textContent = $("pickup-input").value;
    $("confirmation").hidden = false;
  }

  // ----- events -----
  $("category-filter").addEventListener("change", renderProducts);
  $("sort").addEventListener("change", renderProducts);
  $("product-list").addEventListener("click", (e) => {
    const btn = e.target.closest('[data-testid="add-to-cart"]');
    if (btn) addToCart(btn.closest('[data-testid="product"]').dataset.id);
  });
  $("cart-items").addEventListener("click", (e) => {
    const btn = e.target.closest('[data-testid="remove-item"]');
    if (btn) removeFromCart(btn.closest('[data-testid="cart-item"]').dataset.id);
  });
  $("cart-items").addEventListener("change", (e) => {
    if (!e.target.matches('[data-testid="qty-input"]')) return;
    const id = e.target.closest('[data-testid="cart-item"]').dataset.id;
    const qty = Math.max(1, Math.min(20, parseInt(e.target.value, 10) || 1));
    state.cart.set(id, qty);
    e.target.value = qty;
    updateTotals();
  });
  $("coupon-form").addEventListener("submit", (e) => { e.preventDefault(); applyCoupon($("coupon-input").value); });
  $("checkout-button").addEventListener("click", () => $("checkout-dialog").showModal());
  $("checkout-cancel").addEventListener("click", () => $("checkout-dialog").close());
  $("checkout-form").addEventListener("submit", (e) => { if (!validate()) e.preventDefault(); else { e.preventDefault(); placeOrder(); } });
  $("cart-button").addEventListener("click", () => document.getElementById("cart").scrollIntoView({ behavior: "smooth" }));
  $("new-order").addEventListener("click", () => location.reload());

  renderProducts();
  updateTotals();
})();
