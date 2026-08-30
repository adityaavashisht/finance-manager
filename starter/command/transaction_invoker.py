# transaction_invoker.py

class TransactionInvoker:
    """Executes commands and maintains the undo/redo history."""

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def run(self, command):
        """Execute a command and remember it so it can be undone."""
        command.execute()
        self._undo_stack.append(command)
        # A new command invalidates any future we could have redone into.
        self._redo_stack.clear()
        return command

    def undo(self):
        """Undo the most recent command; return it, or None if there is none."""
        if not self._undo_stack:
            return None
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo(self):
        """Re-execute the most recently undone command."""
        if not self._redo_stack:
            return None
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return command

    def can_undo(self):
        return bool(self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)

    @property
    def history(self):
        """Commands that can still be undone, oldest first."""
        return tuple(self._undo_stack)