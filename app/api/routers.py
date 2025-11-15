from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text

from app.db import models, schemas
from app.db.session import get_db
from app.api.dependencies import get_api_key
from app.services.buildings import BuildingService, get_building_service
from app.services.organizations import OrganizationService, get_organization_service

router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(get_api_key)]
)


@router.get("/buildings/", response_model=List[schemas.Building])
def read_buildings(
    skip: int = 0, 
    limit: int = 100, 
    service: BuildingService = Depends(get_building_service)
):
    """
    Retrieve a list of buildings with their associated organizations.
    """
    return service.get_all_buildings(skip=skip, limit=limit)


@router.get("/organizations/{organization_id}", response_model=schemas.Organization)
def read_organization(
    organization_id: int, 
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Retrieve a single organization by its ID.
    """
    return service.get_organization_by_id(organization_id)


@router.get("/buildings/{building_id}/organizations/", response_model=List[schemas.Organization])
def read_organizations_in_building(
    building_id: int, 
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Retrieve all organizations located in a specific building.
    """
    return service.get_organizations_in_building(building_id)


@router.get("/activities/{activity_id}/organizations/", response_model=List[schemas.Organization])
def read_organizations_by_activity(
    activity_id: int, 
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Retrieve all organizations associated with a specific activity.
    """
    return service.get_organizations_by_activity(activity_id)


@router.get("/organizations/search/name/", response_model=List[schemas.Organization])
def search_organizations_by_name(
    name: str, 
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Search for organizations by a partial name match.
    """
    return service.search_by_name(name)


@router.get("/organizations/search/activity/", response_model=List[schemas.Organization])
def search_organizations_by_activity_tree(
    activity_id: int, 
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Search for organizations by a given activity, including all its sub-activities.
    """
    return service.search_by_activity_tree(activity_id)


@router.get("/organizations/search/location/", response_model=List[schemas.Organization])
def search_organizations_by_location(
    latitude: float = Query(..., description="Latitude of the search center"),
    longitude: float = Query(..., description="Longitude of the search center"),
    radius: float = Query(..., description="Search radius in kilometers"),
    service: OrganizationService = Depends(get_organization_service)
):
    """
    Search for organizations within a given radius from a central point.
    """
    return service.search_by_location(latitude, longitude, radius)
