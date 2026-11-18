from playwright.sync_api import Page


class CheckoutPage:
    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_test_id("checkout-dialog")
        self.name = page.get_by_test_id("name-input")
        self.phone = page.get_by_test_id("phone-input")
        self.pickup = page.get_by_test_id("pickup-input")
        self.name_error = page.get_by_test_id("name-error")
        self.phone_error = page.get_by_test_id("phone-error")
        self.pickup_error = page.get_by_test_id("pickup-error")
        self.place_order_button = page.get_by_test_id("place-order")
        self.confirmation = page.get_by_test_id("confirmation")
        self.order_number = page.get_by_test_id("order-number")
        self.order_total = page.get_by_test_id("order-total")
        self.order_pickup = page.get_by_test_id("order-pickup")

    def fill(self, name: str = "", phone: str = "", pickup: str = "") -> "CheckoutPage":
        self.name.fill(name)
        self.phone.fill(phone)
        if pickup:
            self.pickup.fill(pickup)
        return self

    def submit(self) -> None:
        self.place_order_button.click()
