from dataclasses import dataclass

@dataclass
class User:
    id_user: int
    username: str
    password: str
    contact_info: str
    id_role: int
    name_role: str