import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
