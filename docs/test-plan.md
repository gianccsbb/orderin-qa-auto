# Test plan: Quebra-Mar pickup ordering (staging v0.9)

## Scope
The customer flow for ordering ahead and picking up at the café: browse menu → filter/sort → cart → coupon → checkout form → confirmation.
**Out of scope:** payment (orders are paid at pickup), admin panel, load testing.

## Approach
- **Automated end-to-end UI tests** with Playwright + pytest, written in the Page Object pattern (`tests/pages/`), so tests describe user actions and selectors live in one place.
- Tests use stable `data-testid` attributes instead of CSS classes or text that may change.
- Every test starts from a fresh page (no shared state between tests), so tests can run in any order.
- **Known bugs stay in the suite** as `xfail(strict=True)` with the bug ID. The suite is green while the bugs are open. When a developer fixes one, its test passes unexpectedly and the run fails, reminding us to remove the marker. `pytest --runxfail` shows every open bug as a real failure.
- **Boundary values** are tested where rules have limits: quantity 0 / 1 / 20 / 99, pickup 06:30 / 07:00 / 18:59 / 19:00 / 22:15.
- One full flow runs on a **phone-sized screen** (390×844, touch).

## Test cases
| Area | Test | Type |
|---|---|---|
| Menu | All 8 products are listed | Positive |
| Menu | Category filter: Cafés 3, Padaria 3, Doces 2, Todas 8 | Positive (parametrized) |
| Menu | Sort by name is alphabetical | Positive |
| Menu | Sort by price is ascending → **BUG-001** | Positive |
| Cart | Starts empty, checkout disabled | Positive |
| Cart | Adding items updates badge, total, checkout state | Positive |
| Cart | Changing quantity updates total | Positive |
| Cart | Quantity is kept between 1 and 20 (99→20, 0→1, −4→1) | Boundary |
| Cart | Removing an item updates total and badge → **BUG-004** | Positive |
| Coupon | Valid coupon gives 10% off; case and spaces don't matter | Positive (parametrized) |
| Coupon | Invalid coupon shows error and keeps price | Negative |
| Coupon | Same coupon can't be applied twice → **BUG-002** | Negative |
| Checkout | Empty form shows all three errors | Negative |
| Checkout | Pickup outside 7h–19h is rejected | Boundary / negative |
| Checkout | Pickup at 07:00 and 18:59 is accepted | Boundary |
| Checkout | Phone with letters is rejected → **BUG-003** | Negative |
| Checkout | Valid order shows confirmation with number `QM-####`, correct total and pickup time | Positive |
| Mobile | Full order with coupon on a 390 px screen → found **BUG-005** (fixed) | End-to-end |

## Results (latest run)
**24 passed · 5 expected failures (4 open bugs) · 0 unexpected failures**, about 15 s on Chromium.
See `reports/report.html` for the full HTML report.

## Entry / exit criteria
- **Entry:** build deployed to staging, smoke test (menu loads) passes.
- **Exit for release:** no open Critical or High bugs. Current status: **not ready**, because BUG-002 (Critical) and BUG-004 (High) are open.
