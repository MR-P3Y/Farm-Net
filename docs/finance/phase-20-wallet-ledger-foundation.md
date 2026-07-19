# Phase 20.3 Wallet Accounts and Double-Entry Ledger Foundation

## Implemented Database Foundation

Migration `c7e8a1f20303` adds three tables:

1. `finance_wallet_accounts`
   - user-owned or system account identity;
   - accounting kind and explicit purpose;
   - one `TOMAN` account per owner/purpose;
   - active, frozen, and closed lifecycle without storing a mutable balance.
2. `finance_ledger_transactions`
   - unique journal number and idempotency key;
   - immutable source type/id and event identity;
   - positive, equal debit and credit totals;
   - actor, trace, posting time, and optional one-to-one reversal reference;
   - `TOMAN` only.
3. `finance_ledger_entries`
   - ordered debit or credit rows;
   - positive `TOMAN` amount;
   - account and journal foreign keys protected with `RESTRICT`;
   - unique row sequence inside each journal.

## Accounting Boundaries

- The ledger—not a mutable wallet balance—is the source of truth.
- A posted journal and its entries cannot be updated or deleted through the
  ORM. A correction must be a new balanced reversal/adjustment journal.
- Database constraints require positive and equal transaction totals and
  positive entry amounts.
- Cross-row debit/credit summation, exact account-side rules, row locking, and
  atomic posting will be enforced by the posting service in Step 20.4.
- This step creates no account rows, ledger posts, balance API, user wallet UI,
  payment, payout, or settlement.

## Account Purposes

The typed foundation distinguishes provider pending, available, and reserved
payables; customer funds; platform cash and revenue; deposit liability; refund
clearing; and payout clearing. Rental deposit liability is therefore separate
from provider revenue by design.

## Permissions

- `wallet.read_own`: base user, seller, service provider, lessor, consultant
- `finance.wallets.read`: Finance Admin/Admin/Super Admin as seeded
- `finance.ledger.read`: Finance Admin/Admin/Super Admin as seeded
- `finance.ledger.reconcile`: Finance Admin/Admin/Super Admin as seeded
- `finance.ledger.post_internal`: intentionally not granted to ordinary or
  Finance Admin roles; reserved for internal trusted posting paths and Super
  Admin until a narrower machine identity exists

## Verification

- Ruff and compileall: passed
- focused foundation/finance tests: 24 passed
- full Backend: 88 passed with 16 existing UTC deprecation warnings
- Alembic: `c7e8a1f20303 (head)`
- Auth seed twice: identical, 12 roles and 246 permissions
- Runtime tables: all three present
- Runtime permissions: all five present
- health: app/database/Redis `ok`
- Alembic metadata check reported only four pre-existing unique-index naming
  differences in Consultant/Services tables; it reported no Finance model or
  migration difference.
