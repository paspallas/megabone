from megabone.qt import QUndoCommand


class DocumentCommand(QUndoCommand):
    """Base for all undoable document operations"""

    def __init__(self, document, description: str):
        super().__init__(description)
        self._document = document
