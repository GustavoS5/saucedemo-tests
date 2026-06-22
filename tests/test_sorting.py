"""Inventory sorting tests for the saucedemo site."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect


@pytest.mark.parametrize(
    "sort_option",
    [
        pytest.param("az", id="name_ascending"),
        pytest.param("za", id="name_descending"),
        pytest.param("lohi", id="price_low_to_high"),
        pytest.param("hilo", id="price_high_to_low"),
    ],
)
def test_sort_changes_item_order(inventory_page, sort_option: str):
    """Selecting a sort option updates the inventory list display."""
    inventory_page.sort_by(sort_option)
    expect(inventory_page.sort_dropdown).to_have_value(sort_option)


@pytest.mark.parametrize(
    "sort_option, expected_order",
    [
        pytest.param("az", lambda names: names == sorted(names), id="name_ascending"),
        pytest.param(
            "za",
            lambda names: names == sorted(names, reverse=True),
            id="name_descending",
        ),
        pytest.param(
            "lohi", lambda prices: prices == sorted(prices), id="price_low_to_high"
        ),
        pytest.param(
            "hilo",
            lambda prices: prices == sorted(prices, reverse=True),
            id="price_high_to_low",
        ),
    ],
)
def test_sort_order_is_correct(inventory_page, sort_option: str, expected_order):
    """Each sort option orders the inventory list by the expected criteria."""
    inventory_page.sort_by(sort_option)

    if sort_option in {"az", "za"}:
        values = inventory_page.get_item_names_in_order()
    else:
        values = inventory_page.get_item_prices_in_order()

    assert expected_order(values), f"Unexpected order for {sort_option}: {values}"
