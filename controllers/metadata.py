from sqlalchemy.orm import Session
from models.metadata import Location, Country, Town
from schemas.metadata import LocationCreate, CountryCreate, TownCreate, CountryUpdate, TownUpdate, LocationUpdate
from typing import List, Optional


class LocationController:
    """
    Controller for managing metadata related to locations, countries, and towns.
    Provides CRUD operations for each entity.
    """

    def __init__(self, db: Session):
        self.db = db

    # Location CRUD operations
    async def create_location(self, location:LocationCreate):
        """
        Create a new location in the database.
        :param location: LocationCreate schema containing location details.
        :return: Created Location object.
        """
        db_location = Location(**location.dict())
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location
    
    async def get_location(self, location_id: str) -> Optional[Location]:
        """
        Retrieve a location by its ID.
        :param location_id: Unique identifier for the location.
        :return: Location object if found, else None.
        """
        return self.db.query(Location).filter(Location.location_id == location_id).first()
    
    async def get_locations(self, skip: int = 0, limit: int = 100) -> List[Location]:
        """
        Retrieve a list of locations with pagination.
        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of Location objects.
        """
        return self.db.query(Location).offset(skip).limit(limit).all()
    
    async def patch_location(self, location_id: str, location_update: LocationUpdate) -> Optional[Location]:
        """
        Partially update an existing location.
        :param location_id: Unique identifier for the location (primary key, not modified).
        :param location_update: LocationUpdate schema containing fields to update.
        :return: Updated Location object if found, else None.
        """
        db_location = await self.get_location(location_id)
        if db_location:
            # Only update fields that are provided (not None)
            update_data = {k: v for k, v in location_update.dict().items() if v is not None}
            for key, value in update_data.items():
                setattr(db_location, key, value)
            self.db.commit()
            self.db.refresh(db_location)
            return db_location
        return None
    
    async def delete_location(self, location_id: str) -> Optional[Location]:
        """
        Delete a location by its ID.
        :param location_id: Unique identifier for the location.
        :return: Deleted Location object if found, else None.
        """
        db_location = self.get_location(location_id)
        if db_location:
            self.db.delete(db_location)
            self.db.commit()
            return db_location
        return None

class CountryController:
    """
    Controller for managing countries and towns.
    Provides CRUD operations for countries and towns.
    """

    def __init__(self, db: Session):
        self.db = db

    # Country CRUD operations
    async def create_country(self, country: CountryCreate):
        """
        Create a new country in the database.
        :param country: CountryCreate schema containing country details.
        :return: Created Country object.
        """
        db_country = Country(**country.dict())
        self.db.add(db_country)
        self.db.commit()
        self.db.refresh(db_country)
        return db_country
    
    async def get_country(self, country_code: str) -> Optional[Country]:
        """
        Retrieve a country by its code.
        :param country_code: Unique identifier for the country.
        :return: Country object if found, else None.
        """
        return self.db.query(Country).filter(Country.country_code == country_code).first()
    
    async def get_countries(self, skip: int = 0, limit: int = 100) -> List[Country]:
        """
        Retrieve a list of countries with pagination.
        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of Country objects.
        """
        return self.db.query(Country).offset(skip).limit(limit).all()
    
    async def patch_country(self, country_code: str, country_update: CountryUpdate) -> Optional[Country]:
        """
        Partially update an existing country.
        :param country_code: Unique identifier for the country.
        :param country_update: CountryUpdate schema containing fields to update.
        :return: Updated Country object if found, else None.
        """
        db_country = await self.get_country(country_code)
        if db_country:
            # Only update fields that are provided (not None)
            update_data = {k: v for k, v in country_update.dict().items() if v is not None}
            for key, value in update_data.items():
                setattr(db_country, key, value)
            self.db.commit()
            self.db.refresh(db_country)
            return db_country
        return None
    
    async def delete_country(self, country_code: str) -> Optional[Country]:
        """
        Delete a country by its code.
        :param country_code: Unique identifier for the country.
        :return: Deleted Country object if found, else None.
        """
        db_country = self.get_country(country_code)
        if db_country:
            self.db.delete(db_country)
            self.db.commit()
            return db_country
        return None

class TownController:
    """
    Controller for managing towns within countries.
    Provides CRUD operations for towns.
    """
    def __init__(self, db: Session):
        self.db = db

    # Town CRUD operations
    async def create_town(self, town: TownCreate):
        """
        Create a new town in the database.
        :param town: TownCreate schema containing town details.
        :return: Created Town object.
        """
        db_town = Town(**town.dict())
        self.db.add(db_town)
        self.db.commit()
        self.db.refresh(db_town)
        return db_town
    
    async def get_town(self, country_code: str, town_code: str) -> Optional[Town]:
        """
        Retrieve a town by its country code and town code.
        :param country_code: Unique identifier for the country.
        :param town_code: Unique identifier for the town.
        :return: Town object if found, else None.
        """
        return self.db.query(Town).filter(
            Town.country_code == country_code,
            Town.town_code == town_code
        ).first()
    
    async def get_towns(self, skip: int = 0, limit: int = 100) -> List[Town]:
        """
        Retrieve a list of towns with pagination.
        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :return: List of Town objects.
        """
        return self.db.query(Town).offset(skip).limit(limit).all()
    
    async def patch_town(self, country_code: str, town_code: str, town_update: TownUpdate) -> Optional[Town]:
        """
        Partially update an existing town.
        :param country_code: Unique identifier for the country (primary key, not modified).
        :param town_code: Unique identifier for the town (primary key, not modified).
        :param town_update: TownUpdate schema containing fields to update.
        :return: Updated Town object if found, else None.
        """
        db_town = await self.get_town(country_code, town_code)
        if db_town:
            # Only update fields that are provided (not None)
            update_data = {k: v for k, v in town_update.dict().items() if v is not None}
            for key, value in update_data.items():
                setattr(db_town, key, value)
            self.db.commit()
            self.db.refresh(db_town)
            return db_town
        return None
    
    async def delete_town(self, country_code: str, town_code: str) -> Optional[Town]:
        """"
        Delete a town by its country code and town code.
        :param country_code: Unique identifier for the country.
        :param town_code: Unique identifier for the town.
        :return: Deleted Town object if found, else None.
        """
        db_town = self.get_town(country_code, town_code)
        if db_town:
            self.db.delete(db_town)
            self.db.commit()
            return db_town
        return None
    
