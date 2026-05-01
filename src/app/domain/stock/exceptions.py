class StockError(Exception):
    """庫存模組錯誤基底類別。"""


class InsufficientStockError(StockError):
    """嘗試出庫/調整時存量不足。"""

    def __init__(self, item_id, location_id, current: int, requested: int):
        self.item_id = item_id
        self.location_id = location_id
        self.current = current
        self.requested = requested
        super().__init__(
            f"Insufficient stock: item={item_id} location={location_id} "
            f"current={current} requested={requested}"
        )
