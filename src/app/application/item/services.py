from uuid import UUID, uuid4
from typing import List, Optional
from src.app.domain.item.models import Item
from src.app.infrastructure.repositories.item_repository import ItemRepository
from src.app.api.v1.schemas.item import ItemRead


class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self._item_repo = item_repo

    async def get_items(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[List[ItemRead], int]:
        items, total = await self._item_repo.get_list(skip, limit)
        return [ItemRead.model_validate(i) for i in items], total

    async def get_item(self, item_id: UUID) -> Optional[ItemRead]:
        item = await self._item_repo.get_by_id(item_id)
        if not item:
            return None
        return ItemRead.model_validate(item)

    async def create_item(
        self, name: str, note: Optional[str], creator_id: UUID
    ) -> ItemRead:
        new_item = Item(
            id=uuid4(),
            name=name,
            note=note,
            created_by=creator_id,
        )
        created = await self._item_repo.create(new_item)
        return ItemRead.model_validate(created)

    async def update_item(
        self, item_id: UUID, name: str, note: Optional[str], updater_id: UUID
    ) -> Optional[ItemRead]:
        item = await self._item_repo.get_by_id(item_id)
        if not item:
            return None

        item.name = name
        item.note = note
        item.updated_by = updater_id
        updated = await self._item_repo.update(item)
        return ItemRead.model_validate(updated)

    async def delete_item(self, item_id: UUID) -> bool:
        item = await self._item_repo.get_by_id(item_id)
        if not item:
            return False
        await self._item_repo.delete(item)
        return True
