import pytest
from playwright.sync_api import expect


@pytest.fixture
def cart_of_20(shop):
    shop.add("Bolo de rolo (fatia)", times=2)  # R$ 20,00
    expect(shop.subtotal).to_have_text("R$ 20,00")
    return shop


@pytest.mark.parametrize("code", ["BOAVIAGEM10", "boaviagem10", "  BoaViagem10  "])
def test_valid_coupon_gives_10_percent_off(cart_of_20, code):
    cart_of_20.apply_coupon(code)
    expect(cart_of_20.coupon_msg).to_contain_text("10%")
    expect(cart_of_20.total).to_have_text("R$ 18,00")


def test_invalid_coupon_shows_error_and_keeps_price(cart_of_20):
    cart_of_20.apply_coupon("CUPOMFALSO")
    expect(cart_of_20.coupon_msg).to_have_text("Cupom inválido.")
    expect(cart_of_20.total).to_have_text("R$ 20,00")


@pytest.mark.xfail(strict=True, reason="BUG-002: the same coupon can be applied again and the discount stacks")
def test_same_coupon_cannot_be_applied_twice(cart_of_20):
    cart_of_20.apply_coupon("BOAVIAGEM10")
    cart_of_20.apply_coupon("BOAVIAGEM10")
    expect(cart_of_20.total).to_have_text("R$ 18,00", timeout=1500)
