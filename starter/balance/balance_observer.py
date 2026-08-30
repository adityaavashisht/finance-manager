# balance_observer.py

class IBalanceObserver:
    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    """Prints the running balance every time a transaction is applied."""

    def __init__(self, writer=print):
        self.writer = writer

    def update(self, balance, transaction):
        """Print balance update message."""
        self.writer(
            f"[Balance] {transaction} applied -> net balance is now ${balance:.2f}"
        )


class LowBalanceAlertObserver(IBalanceObserver):
    """Raises an alert whenever the balance sits below ``threshold``."""

    def __init__(self, threshold, notifier=print):
        self.threshold = threshold
        self.notifier = notifier
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
        if self.alert_triggered:
            self.notifier(
                f"[ALERT] Balance ${balance:.2f} is below the "
                f"${self.threshold:.2f} threshold!"
            )