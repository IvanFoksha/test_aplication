from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.buildings import BuildingRepository


class BuildingService:
    def __init__(self, building_repo: BuildingRepository):
        self.building_repo = building_repo

    def get_all_buildings(self, skip: int = 0, limit: int = 100):
        return self.building_repo.get_all_with_organizations(skip=skip, limit=limit)


def get_building_service(db: Session = Depends(get_db)) -> BuildingService:
    repo = BuildingRepository(db)
    return BuildingService(repo)
