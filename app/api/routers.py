from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from app.db import models, schemas
from app.db.session import get_db
from app.api.dependencies import get_api_key

router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(get_api_key)]
)

@router.get("/buildings/", response_model=List[schemas.Building])
def read_buildings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of buildings with their associated organizations.
    """
    buildings = (
        db.query(models.Building)
        .options(joinedload(models.Building.organizations))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return buildings


@router.get("/organizations/{organization_id}", response_model=schemas.Organization)
def read_organization(organization_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single organization by its ID.
    """
    organization = (
        db.query(models.Organization)
        .options(
            joinedload(models.Organization.building),
            joinedload(models.Organization.phone_numbers),
            joinedload(models.Organization.activities),
        )
        .filter(models.Organization.id == organization_id)
        .first()
    )
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.get("/buildings/{building_id}/organizations/", response_model=List[schemas.Organization])
def read_organizations_in_building(building_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all organizations located in a specific building.
    """
    building = db.query(models.Building).filter(models.Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    organizations = (
        db.query(models.Organization)
        .filter(models.Organization.building_id == building_id)
        .options(
            joinedload(models.Organization.phone_numbers),
            joinedload(models.Organization.activities)
        )
        .all()
    )
    return organizations


@router.get("/activities/{activity_id}/organizations/", response_model=List[schemas.Organization])
def read_organizations_by_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all organizations associated with a specific activity.
    """
    activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    return activity.organizations


@router.get("/organizations/search/name/", response_model=List[schemas.Organization])
def search_organizations_by_name(name: str, db: Session = Depends(get_db)):
    """
    Search for organizations by a partial name match.
    """
    organizations = (
        db.query(models.Organization)
        .filter(models.Organization.name.ilike(f"%{name}%"))
        .options(
            joinedload(models.Organization.building),
            joinedload(models.Organization.phone_numbers),
            joinedload(models.Organization.activities),
        )
        .all()
    )
    return organizations


@router.get("/organizations/search/activity/", response_model=List[schemas.Organization])
def search_organizations_by_activity_tree(activity_id: int, db: Session = Depends(get_db)):
    """
    Search for organizations by a given activity, including all its sub-activities.
    """
    # Check if the root activity exists
    root_activity = db.query(models.Activity).filter(models.Activity.id == activity_id).first()
    if not root_activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Recursive CTE to find all descendant activities
    # NOTE: This syntax is specific to PostgreSQL.
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

    activity_ids_result = db.execute(cte_query, {"activity_id": activity_id}).fetchall()
    activity_ids = [row[0] for row in activity_ids_result]

    # Find organizations linked to any of these activities
    organizations = (
        db.query(models.Organization)
        .join(models.organization_activity_association)
        .filter(models.organization_activity_association.c.activity_id.in_(activity_ids))
        .options(
            joinedload(models.Organization.building),
            joinedload(models.Organization.phone_numbers),
            joinedload(models.Organization.activities),
        )
        .distinct()
        .all()
    )

    return organizations


@router.get("/organizations/search/location/", response_model=List[schemas.Organization])
def search_organizations_by_location(
    latitude: float = Query(..., description="Latitude of the search center"),
    longitude: float = Query(..., description="Longitude of the search center"),
    radius: float = Query(..., description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Search for organizations within a given radius from a central point.
    This uses the Haversine formula for distance calculation.
    """
    # Haversine formula in SQL for PostgreSQL to calculate distance in kilometers.
    # 6371 is the Earth's radius in kilometers.
    distance_sql = text("""
        6371 * acos(
            cos(radians(:lat)) * cos(radians(b.latitude)) *
            cos(radians(b.longitude) - radians(:lon)) +
            sin(radians(:lat)) * sin(radians(b.latitude))
        )
    """)

    # Find building IDs within the given radius
    buildings_within_radius = (
        db.query(models.Building.id)
        .from_statement(
            text("SELECT b.id FROM buildings b WHERE (:distance_sql) < :radius")
            .bindparams(distance_sql=distance_sql)
        )
        .params(lat=latitude, lon=longitude, radius=radius)
        .all()
    )

    building_ids = [row[0] for row in buildings_within_radius]
    
    if not building_ids:
        return []

    # Get organizations in those buildings
    organizations = (
        db.query(models.Organization)
        .filter(models.Organization.building_id.in_(building_ids))
        .options(
            joinedload(models.Organization.building),
            joinedload(models.Organization.phone_numbers),
            joinedload(models.Organization.activities),
        )
        .all()
    )

    return organizations
