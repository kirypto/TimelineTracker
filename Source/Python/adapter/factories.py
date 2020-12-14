from adapter.persistence.in_memory_repositories import InMemoryLocationRepository, InMemoryTravelerRepository, InMemoryEventRepository
from adapter.persistence.json_file_repositories import JsonFileLocationRepository, JsonFileTravelerRepository, JsonFileEventRepository
from domain.persistence.repositories import TravelerRepository, LocationRepository, EventRepository


class RepositoriesFactory:
    _traveler_repo: TravelerRepository
    _location_repo: LocationRepository
    _event_repo: EventRepository

    @property
    def location_repo(self) -> LocationRepository:
        return self._location_repo

    @property
    def traveler_repo(self) -> TravelerRepository:
        return self._traveler_repo

    @property
    def event_repo(self) -> EventRepository:
        return self._event_repo

    def __init__(self, repository_type: str, **kwargs) -> None:
        if repository_type == "json":
            self._location_repo = JsonFileLocationRepository(**kwargs)
            self._traveler_repo = JsonFileTravelerRepository(**kwargs)
            self._event_repo = JsonFileEventRepository(**kwargs)
        elif repository_type == "memory":
            if len(kwargs) > 0:
                raise ValueError(f"In memory repositories do not required additional params, these were given: {kwargs.keys()}")
            self._location_repo = InMemoryLocationRepository()
            self._traveler_repo = InMemoryTravelerRepository()
            self._event_repo = InMemoryEventRepository()
        else:
            raise ValueError(f"Unsupported repository type {repository_type}")
