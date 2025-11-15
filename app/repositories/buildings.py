from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text
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

    def get_ids_within_radius(self, latitude: float, longitude: float, radius: float) -> list[int]:
        """
        Calculates and finds building IDs within a given radius from a central point.
        Uses the Haversine formula.
        """
        distance_sql = text("""
            6371 * acos(
                cos(radians(:lat)) * cos(radians(latitude)) *
                cos(radians(longitude) - radians(:lon)) +
                sin(radians(:lat)) * sin(radians(latitude))
            )
        """)

        buildings_within_radius = (
            self.db.query(self.model.id)
            .from_statement(
                text("SELECT id FROM buildings WHERE (:distance_sql) < :radius")
                .bindparams(distance_sql=distance_sql)
            )
            .params(lat=latitude, lon=longitude, radius=radius)
            .all()
        )
        return [row[0] for row in buildings_within_radius]
