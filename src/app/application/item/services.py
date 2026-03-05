from uuid import UUID, uuid4
from typing import List, Optional
from src.app.domain.item.models import Item
from src.app.infrastructure.repositories.item_repository import ItemRepository


class ItemService:
    def __init__(self, item_repo: ItemRepository):
        self._item_repo = item_repo

    async def get_items(self, skip: int = 0, limit: int = 10) -> tuple[List[Item], int]:
        return await self._item_repo.get_list(skip, limit)

    async def get_item(self, item_id: UUID) -> Optional[Item]:
        return await self._item_repo.get_by_id(item_id)

    async def create_item(self, name: str, note: Optional[str], creator_id: UUID) -> Item:
        new_item = Item(
            id=uuid4(),
            name=name,
            note=note,
            created_by=creator_id,
        )
        return await self._item_repo.create(new_item)

    async def update_item(
        self, item_id: UUID, name: str, note: Optional[str], updater_id: UUID
    ) -> Optional[Item]:
        item = await self._item_repo.get_by_id(item_id)
        if not item:
            return None

        item.name = name
        item.note = note
        item.updated_by = updater_id
        return await self._item_repo.update(item)

    async def delete_item(self, item_id: UUID) -> bool:
        item = await self._item_repo.get_by_id(item_id)
        if not item:
            return False
        await self._item_repo.delete(item)
        return True
