from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import models
from app.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[models.Activity]):
    def __init__(self, db: Session):
        super().__init__(models.Activity, db)

    def get_descendant_ids(self, activity_id: int) -> list[int]:
        """
        Performs a recursive CTE query to find all descendant activity IDs
        for a given parent activity.
        """
        cte_query = text("""
            WITH RECURSIVE activity_tree AS (
                SELECT id
                FROM activities
                WHERE id = :activity_id
                UNION ALL
                SELECT a.id
                FROM activities a
                JOIN activity_tree at ON a.parent_id = at.id
            )
            SELECT id FROM activity_tree
        """)

        result = self.db.execute(cte_query, {"activity_id": activity_id}).fetchall()
        return [row[0] for row in result]
