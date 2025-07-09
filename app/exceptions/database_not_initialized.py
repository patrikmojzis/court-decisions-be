class DatabaseNotInitialized(RuntimeError):

    def __init__(self):
        super().__init__("Database not initialized")