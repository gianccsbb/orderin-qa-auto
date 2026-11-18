import re

import pytest
from playwright.sync_api import expect

from pages.shop_page import ShopPage

VALID = {"name": "Ana Souza", "phone": "(81) 9 8765-4321", "pickup": "08:30"}


@pytest.fixture
def checkout(shop):
    shop.add("Café coado")
    shop.add("Tapioca de queijo coalho")   # R$ 20,00
    return shop.go_to_checkout()


def test_empty_form_shows_all_errors(checkout):
    checkout.submit()
    expect(checkout.name_error).to_have_text("Informe seu nome.")
    expect(checkout.phone_error).to_have_text("Telefone inválido.")
    expect(checkout.pickup_error).to_have_text("Escolha um horário.")
    expect(checkout.confirmation).to_be_hidden()


@pytest.mark.parametrize("pickup", ["06:30", "19:00", "22:15"])
def test_pickup_outside_opening_hours_is_rejected(checkout, pickup):
    checkout.fill(VALID["name"], VALID["phone"], pickup).submit()
    expect(checkout.pickup_error).to_have_text("Escolha um horário entre 7h e 19h.")
    expect(checkout.confirmation).to_be_hidden()


@pytest.mark.parametrize("pickup", ["07:00", "18:59"])
def test_pickup_at_the_edges_of_opening_hours_is_accepted(checkout, pickup):
    checkout.fill(VALID["name"], VALID["phone"], pickup).submit()
    expect(checkout.confirmation).to_be_visible()


@pytest.mark.xfail(strict=True, reason="BUG-003: phone validation only checks length, so letters are accepted")
@pytest.mark.parametrize("phone", ["abcdefghijk", "81-ABCD-9999"])
def test_phone_with_letters_is_rejected(checkout, phone):
    checkout.fill(VALID["name"], phone, VALID["pickup"]).submit()
    expect(checkout.phone_error).to_have_text("Telefone inválido.", timeout=1500)


def test_successful_order_shows_confirmation(checkout):
    checkout.fill(**VALID).submit()
    expect(checkout.confirmation).to_be_visible()
    expect(checkout.order_number).to_have_text(re.compile(r"^QM-\d{4}$"))
    expect(checkout.order_total).to_have_text("R$ 20,00")
    expect(checkout.order_pickup).to_have_text("08:30")


def test_full_order_on_a_phone_screen(browser, base_url):
    context = browser.new_context(base_url=base_url, viewport={"width": 390, "height": 844},
                                  is_mobile=True, has_touch=True)
    page = context.new_page()
    shop = ShopPage(page).open()
    shop.add("Pão na chapa")
    shop.apply_coupon("BOAVIAGEM10")
    expect(shop.total).to_have_text("R$ 6,30")
    checkout = shop.go_to_checkout()
    checkout.fill(**VALID).submit()
    expect(checkout.order_total).to_have_text("R$ 6,30")
    context.close()
