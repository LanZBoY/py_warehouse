from enum import Enum


class StockMovementType(str, Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    ADJUST = "ADJUST"
