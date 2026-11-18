"""Page object for the menu and cart. Tests talk to this class, not to selectors,
so a UI change only needs fixing in one place."""
from playwright.sync_api import Locator, Page


class ShopPage:
    def __init__(self, page: Page):
        self.page = page
        self.products = page.get_by_test_id("product")
        self.category_filter = page.get_by_test_id("category-filter")
        self.sort_select = page.get_by_test_id("sort")
        self.cart_items = page.get_by_test_id("cart-item")
        self.cart_count = page.get_by_test_id("cart-count")
        self.cart_empty = page.get_by_test_id("cart-empty")
        self.subtotal = page.get_by_test_id("subtotal")
        self.discount = page.get_by_test_id("discount")
        self.total = page.get_by_test_id("total")
        self.coupon_input = page.get_by_test_id("coupon-input")
        self.coupon_apply = page.get_by_test_id("coupon-apply")
        self.coupon_msg = page.get_by_test_id("coupon-msg")
        self.checkout_button = page.get_by_test_id("checkout-button")

    def open(self) -> "ShopPage":
        self.page.goto("/index.html")
        return self

    # ----- menu -----
    def product(self, name: str) -> Locator:
        return self.products.filter(has=self.page.get_by_test_id("product-name").get_by_text(name, exact=True))

    def product_names(self) -> list[str]:
        return self.page.get_by_test_id("product-name").all_inner_texts()

    def product_prices_in_cents(self) -> list[int]:
        return [money_to_cents(t) for t in self.page.get_by_test_id("product-price").all_inner_texts()]

    def filter_by(self, category: str) -> None:
        self.category_filter.select_option(category)

    def sort_by(self, option: str) -> None:
        self.sort_select.select_option(option)

    def add(self, name: str, times: int = 1) -> None:
        for _ in range(times):
            self.product(name).get_by_test_id("add-to-cart").click()

    # ----- cart -----
    def cart_item(self, name: str) -> Locator:
        return self.cart_items.filter(has=self.page.get_by_test_id("cart-item-name").get_by_text(name, exact=True))

    def set_quantity(self, name: str, qty: int | str) -> None:
        field = self.cart_item(name).get_by_test_id("qty-input")
        field.fill(str(qty))
        field.press("Tab")  # 'change' fires on blur, like a real user leaving the field

    def remove(self, name: str) -> None:
        self.cart_item(name).get_by_test_id("remove-item").click()

    def apply_coupon(self, code: str) -> None:
        self.coupon_input.fill(code)
        self.coupon_apply.click()

    def total_in_cents(self) -> int:
        return money_to_cents(self.total.inner_text())

    def go_to_checkout(self):
        from .checkout_page import CheckoutPage
        self.checkout_button.click()
        return CheckoutPage(self.page)


def money_to_cents(text: str) -> int:
    """'R$ 1.234,50' or '− R$ 2,00' -> cents (sign ignored)."""
    digits = text.replace("R$", "").replace("−", "").replace(" ", "").replace(" ", "")
    return round(float(digits.replace(".", "").replace(",", ".")) * 100)
