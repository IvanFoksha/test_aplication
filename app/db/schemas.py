from pydantic import BaseModel
from typing import List, Optional


# Phone Number Schemas
class PhoneNumberBase(BaseModel):
    number: str


class PhoneNumberCreate(PhoneNumberBase):
    pass


class PhoneNumber(PhoneNumberBase):
    id: int
    organization_id: int

    class Config:
        orm_mode = True


# Activity Schemas
class ActivityBase(BaseModel):
    name: str


class ActivityCreate(ActivityBase):
    parent_id: Optional[int] = None


class Activity(ActivityBase):
    id: int
    parent_id: Optional[int] = None
    children: List["Activity"] = []

    class Config:
        orm_mode = True


Activity.update_forward_refs()


# Building Schemas
class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float


class BuildingCreate(BuildingBase):
    pass


class Building(BuildingBase):
    id: int
    organizations: List["Organization"] = []

    class Config:
        orm_mode = True


# Organization Schemas
class OrganizationBase(BaseModel):
    name: str


class OrganizationCreate(OrganizationBase):
    building_id: int


class Organization(OrganizationBase):
    id: int
    building: BuildingBase
    phone_numbers: List[PhoneNumberBase] = []
    activities: List[ActivityBase] = []

    class Config:
        orm_mode = True


Building.update_forward_refs()
