from sqlalchemy.orm import Session, joinedload
from app.db import models
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[models.Organization]):
    def __init__(self, db: Session):
        super().__init__(models.Organization, db)

    def get_by_id_with_details(
        self,
        organization_id: int
    ) -> models.Organization | None:
        return (
            self.db.query(self.model)
            .options(
                joinedload(self.model.building),
                joinedload(self.model.phone_numbers),
                joinedload(self.model.activities),
            )
            .filter(self.model.id == organization_id)
            .first()
        )

    def get_by_building_id(
        self,
        building_id: int
    ) -> list[models.Organization]:
        return (
            self.db.query(self.model)
            .filter(self.model.building_id == building_id)
            .options(
                joinedload(self.model.phone_numbers),
                joinedload(self.model.activities)
            )
            .all()
        )

    def search_by_name(self, name: str) -> list[models.Organization]:
        return (
            self.db.query(self.model)
            .filter(self.model.name.ilike(f"%{name}%"))
            .options(
                joinedload(self.model.building),
                joinedload(self.model.phone_numbers),
                joinedload(self.model.activities),
            )
            .all()
        )

    def get_by_activity_ids(
        self,
        activity_ids: list[int]
    ) -> list[models.Organization]:
        return (
            self.db.query(self.model)
            .join(models.organization_activity_association)
            .filter(
                models.organization_activity_association.c.activity_id.in_(
                    activity_ids
                )
            )
            .options(
                joinedload(self.model.building),
                joinedload(self.model.phone_numbers),
                joinedload(self.model.activities),
            )
            .distinct()
            .all()
        )

    def get_by_building_ids(
        self,
        building_ids: list[int]
    ) -> list[models.Organization]:
        return (
            self.db.query(self.model)
            .filter(self.model.building_id.in_(building_ids))
            .options(
                joinedload(self.model.building),
                joinedload(self.model.phone_numbers),
                joinedload(self.model.activities),
            )
            .all()
        )
