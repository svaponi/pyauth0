class Auth0Error(Exception):
    def __init__(self, status_code: int, code: str, description: str):
        super().__init__(description)
        self.status_code = status_code
        self.code = code
        self.description = description
