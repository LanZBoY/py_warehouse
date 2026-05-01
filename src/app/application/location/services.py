from uuid import UUID, uuid4
from typing import List, Optional
from src.app.domain.location.models import Location
from src.app.infrastructure.repositories.location_repository import LocationRepository
from src.app.api.v1.schemas.location import LocationRead


class LocationService:
    def __init__(self, location_repo: LocationRepository):
        self._location_repo = location_repo

    async def get_locations(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[List[LocationRead], int]:
        locations, total = await self._location_repo.get_list(skip, limit)
        return [LocationRead.model_validate(l) for l in locations], total

    async def get_location(self, location_id: UUID) -> Optional[LocationRead]:
        location = await self._location_repo.get_by_id(location_id)
        if not location:
            return None
        return LocationRead.model_validate(location)

    async def create_location(
        self, name: str, note: Optional[str], creator_id: UUID
    ) -> LocationRead:
        new_location = Location(
            id=uuid4(),
            name=name,
            note=note,
            created_by=creator_id,
        )
        created = await self._location_repo.create(new_location)
        return LocationRead.model_validate(created)

    async def update_location(
        self, location_id: UUID, name: str, note: Optional[str], updater_id: UUID
    ) -> Optional[LocationRead]:
        location = await self._location_repo.get_by_id(location_id)
        if not location:
            return None

        location.name = name
        location.note = note
        location.updated_by = updater_id
        updated = await self._location_repo.update(location)
        return LocationRead.model_validate(updated)

    async def delete_location(self, location_id: UUID) -> bool:
        location = await self._location_repo.get_by_id(location_id)
        if not location:
            return False
        await self._location_repo.delete(location)
        return True
