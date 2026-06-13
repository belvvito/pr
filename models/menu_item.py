from dataclasses import dataclass
from PyQt6.QtGui import QPixmap

@dataclass
class MenuItem:
    id_menu: int
    name_item: str
    description: str
    price: float
    category: str
    quantity: int = 0
    discount: int = 0
    manufacturer: str = ""
    supplier: str = ""
    photo_path: str = "menu.png"
    photo: QPixmap = None

    @property
    def final_price(self) -> float:
        return self.price * (100 - self.discount) / 100