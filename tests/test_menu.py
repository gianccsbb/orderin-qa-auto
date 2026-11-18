import pytest
from playwright.sync_api import expect


def test_menu_lists_all_products(shop):
    expect(shop.products).to_have_count(8)


@pytest.mark.parametrize("category, expected", [("cafes", 3), ("padaria", 3), ("doces", 2), ("all", 8)])
def test_category_filter_shows_only_that_category(shop, category, expected):
    shop.filter_by(category)
    expect(shop.products).to_have_count(expected)


def test_sort_by_name_is_alphabetical(shop):
    shop.sort_by("name")
    names = shop.product_names()
    assert names == sorted(names, key=str.casefold)


@pytest.mark.xfail(strict=True, reason="BUG-001: price sort compares text, so R$ 11,00 comes before R$ 4,00")
def test_sort_by_price_low_to_high(shop):
    shop.sort_by("price-asc")
    prices = shop.product_prices_in_cents()
    assert prices == sorted(prices)
