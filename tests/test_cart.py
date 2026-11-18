import pytest
from playwright.sync_api import expect


def test_cart_starts_empty_with_checkout_disabled(shop):
    expect(shop.cart_empty).to_be_visible()
    expect(shop.cart_count).to_have_text("0")
    expect(shop.checkout_button).to_be_disabled()


def test_adding_items_updates_badge_and_total(shop):
    shop.add("Café coado", times=2)      # 2 × R$ 6,00
    shop.add("Bolo de rolo (fatia)")     # 1 × R$ 10,00
    expect(shop.cart_items).to_have_count(2)
    expect(shop.cart_count).to_have_text("3")
    expect(shop.total).to_have_text("R$ 22,00")
    expect(shop.checkout_button).to_be_enabled()


def test_changing_quantity_updates_total(shop):
    shop.add("Café coado")
    shop.set_quantity("Café coado", 3)
    expect(shop.total).to_have_text("R$ 18,00")
    expect(shop.cart_count).to_have_text("3")


@pytest.mark.parametrize("typed, kept", [("99", "20"), ("0", "1"), ("-4", "1")])
def test_quantity_is_kept_between_1_and_20(shop, typed, kept):
    shop.add("Brigadeiro")
    shop.set_quantity("Brigadeiro", typed)
    expect(shop.cart_item("Brigadeiro").get_by_test_id("qty-input")).to_have_value(kept)


@pytest.mark.xfail(strict=True, reason="BUG-004: removing an item does not recalculate the totals or the badge")
def test_removing_an_item_updates_total_and_badge(shop):
    shop.add("Café coado")
    shop.add("Cappuccino")
    shop.remove("Cappuccino")
    expect(shop.cart_items).to_have_count(1)
    expect(shop.total).to_have_text("R$ 6,00", timeout=1500)
    expect(shop.cart_count).to_have_text("1", timeout=1500)
