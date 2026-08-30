## Reflection

- **Singleton** — one balance, enforced. Trade-off: shared state, so every test needs `reset()` and `clear_observers()`.
- **Adapter** — converts external freelance income into a `Transaction`. Trade-off: `invoice_id` and `description` are dropped.
- **Observer** — printing and low-balance alerts react to changes instead of sitting inside the balance logic; a new alert is just one more class to write.
- **Command** — undo/redo. Chose it over Strategy and Decorator (`PrintObserver` already logs). Trade-off: history grows.
- **Bug while running tests** — my tests reported success without actually running any. `unittest` only searches a folder for tests if that folder has an `__init__.py`, and mine didn't.
