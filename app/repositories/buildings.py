from sqlalchemy.orm import Session, joinedload
from app.db import models
from app.repositories.base import BaseRepository


class BuildingRepository(BaseRepository[models.Building]):
    def __init__(self, db: Session):
        super().__init__(models.Building, db)

    def get_all_with_organizations(self, skip: int = 0, limit: int = 100) -> list[models.Building]:
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.organizations))
            .offset(skip)
            .limit(limit)
            .all()
        )
