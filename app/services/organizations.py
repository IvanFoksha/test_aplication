from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.organizations import OrganizationRepository
from app.repositories.activities import ActivityRepository
from app.repositories.buildings import BuildingRepository


class OrganizationService:
    def __init__(
        self,
        org_repo: OrganizationRepository,
        activity_repo: ActivityRepository,
        building_repo: BuildingRepository,
    ):
        self.org_repo = org_repo
        self.activity_repo = activity_repo
        self.building_repo = building_repo

    def get_organization_by_id(self, organization_id: int):
        organization = self.org_repo.get_by_id_with_details(organization_id)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return organization

    def get_organizations_in_building(self, building_id: int):
        building = self.building_repo.get(building_id)
        if not building:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
        return self.org_repo.get_by_building_id(building_id)

    def get_organizations_by_activity(self, activity_id: int):
        activity = self.activity_repo.get(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        # Leveraging the pre-defined SQLAlchemy relationship for direct access
        return activity.organizations

    def search_by_name(self, name: str):
        return self.org_repo.search_by_name(name)

    def search_by_activity_tree(self, activity_id: int):
        activity = self.activity_repo.get(activity_id)
        if not activity:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

        descendant_ids = self.activity_repo.get_descendant_ids(activity_id)
        return self.org_repo.get_by_activity_ids(descendant_ids)

    def search_by_location(self, latitude: float, longitude: float, radius: float):
        # Haversine formula part is better kept at repository for data-related logic
        # For now, let's assume we get building_ids from a method.
        # This logic needs a home. Let's place it in BuildingRepository.
        building_ids = self.building_repo.get_ids_within_radius(latitude, longitude, radius)
        if not building_ids:
            return []
        return self.org_repo.get_by_building_ids(building_ids)


def get_organization_service(db: Session = Depends(get_db)) -> OrganizationService:
    org_repo = OrganizationRepository(db)
    activity_repo = ActivityRepository(db)
    building_repo = BuildingRepository(db)
    return OrganizationService(org_repo, activity_repo, building_repo)
