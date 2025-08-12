"""Pydantic models for scraped data."""

from collections.abc import Callable
import datetime as dt
from enum import StrEnum
from typing import Annotated, TypeVar

from pydantic import (
    AfterValidator,
    BeforeValidator,
    AliasChoices,
    BaseModel,
    Field,
    ValidationInfo,
    computed_field,
    field_validator,
)

from .utils import allows_none
from .validators import convert_date, soft_validate, validate_state


X = TypeVar("X")
Y = TypeVar("Y")


class Sex(StrEnum):
    """An enumerator for a person's sex.

    Attributes
    ----------
    MALE
        The male sex.
    FEMALE
        The female sex.
    OTHER
        Other sexes.
    """

    MALE = "M"
    FEMALE = "F"
    OTHER = "X"


class Race(StrEnum):
    """An enumerator for a person's race.

    Attributes
    ----------
    ASIAN
        Persons categorized as Asian/Pacific Islander.
    BLACK
        Persons categorized as Black/African American.
    HISPANIC
        Persons categorized as Latino/Hispanic.
    MULTIRACIAL
        Persons of two or more races.
    NATIVE
        Persons categorized as American Indian/Native American/Alaskan Native
    OTHER
        Persons categorized as some other race.
    UNKNOWN
        Persons whose race is unknown.
    WHITE
        Persons categorized as White/Caucasian.
    """

    ASIAN = "A"
    BLACK = "B"
    HISPANIC = "H"
    MULTIRACIAL = "M"
    NATIVE = "I"
    OTHER = "O"
    UNKNOWN = "U"
    WHITE = "W"


State = Annotated[str, AfterValidator(validate_state)]
ZipCode = Annotated[str, Field(pattern=r"^\d{5}(?:-\d{4})?")]


class BookingItem(BaseModel):
    """Pydantic model for an individual booking.

    Attributes
    ----------
    county : str
        The county jail in which the person was booked.
    booking_id : str
        The unique ID for the booking.
    person_id : str
        The unique ID for the person booked.
    booking_num : str | None
        The booking number as assigned by the sheriff.
    booking_date : dt.datetime
        The booking date.
    release_date : dt.datetime | None
        The person's release date.
    held_for : str | None
        The name of the agency the person is being held for, if any.
    first_name : str
        The first name of the person booked.
    middle_name : str | None
        The middle name of the person booked.
    last_name : str
        The last name of the person booked.
    sex : Sex
        The person's sex as recorded by the agency.
    race : Race
        The person's race as recorded by the agency.
    classification : str | None
        The security level classification.
    arresting_agency : str | None
        The arresting agency, if provided.
    address : str | None
        The person's street address as recorded by the agency.
    city : str
        The person's city of residence as recorded by the agency.
    state : State | None
        The person's state of residence as recorded by the agency.
    zipcode : ZipCode | None
        The person's ZIP code as recorded by the agency.
    charges : str
        The persons's charges as reported by the agency.
    bond_total : float | None
        The total bond, if any.
    birth_date : Annotated[dt.datetime, BeforeValidator(convert_date)]
        The person's date of birth as recorded by the agency.
    court_date : dt.datetime | None
        The court date as recorded by the agency, if any.
    """

    county: str
    booking_id: str = Field(validation_alias="BookingID")
    person_id: str = Field(validation_alias="InmateID")
    booking_num: str | None = Field(default=None, validation_alias="BookingNum")
    booking_date: dt.datetime = Field(
        validation_alias=AliasChoices("BookingDate", "bookingDate")
    )
    release_date: dt.datetime | None = Field(
        default=None, validation_alias="ReleaseDate"
    )
    held_for: str | None = Field(default=None, validation_alias="heldfor")
    first_name: str = Field(validation_alias="FName")
    middle_name: str | None = Field(default=None, validation_alias="MName")
    last_name: str = Field(validation_alias="LName")
    sex: Sex = Field(validation_alias=AliasChoices("Sex", "Gender"))
    race: Race = Field(validation_alias="Race")
    classification: str | None = Field(default=None, validation_alias="Classification")
    arresting_agency: str | None = Field(
        default=None, validation_alias="ArrestingAgency"
    )
    address: str | None = Field(default=None, validation_alias="Address")
    city: str = Field(validation_alias="City")
    state: State | None = Field(validation_alias="State")
    zipcode: ZipCode | None = Field(default=None, validation_alias="Zip")
    charges: str = Field(validation_alias="Charges")
    bond_total: float | None = Field(default=None, validation_alias="BondTotal")
    birth_date: Annotated[dt.datetime, BeforeValidator(convert_date)] = Field(
        validation_alias=AliasChoices("dob", "DOB", "BirthDate"),
    )
    court_date: dt.datetime | None = Field(default=None, validation_alias="CourtDate")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def age(self) -> int:
        """Compute the person's age.

        Returns
        -------
        int
            The person's age.
        """
        return int((dt.datetime.now() - self.birth_date).days / 365.24)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        """Return the person's full name.

        Returns
        -------
        str
            The person's full name.
        """
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def mailing_address(self) -> str:
        """Return the full mailing address.

        Returns
        -------
        str
            The full mailing address.
        """
        return f"{self.address}\n{self.city}, {self.state} {self.zipcode if self.zipcode is not None else ''}".strip()

    @field_validator("*", mode="wrap")
    @classmethod
    def soft_validate(
        cls, value: X, handler: Callable[[X], Y], info: ValidationInfo
    ) -> Y | None:
        """Set field to None on validation error if field is optional.

        Parameters
        ----------
        value : X
            The value to validate.
        handler: Callable[[X], Y]
            The validator handler for the current field.
        info : ValidationInfo
            The current validation context.

        Returns
        -------
        Y | None
            The validated value, or None.

        Raises
        ------
        ValueError
            Raised if the field name is missing.
        """
        if info.field_name is None:
            raise ValueError("Field name not defined.")
        if allows_none(cls.model_fields[info.field_name].annotation):
            return None if value == "" else soft_validate(value, handler)
        return handler(value)

    @field_validator("*", mode="before")
    @classmethod
    def strip_string(cls, value: X | str) -> X | str:
        """Strip whitespace from string values.

        Parameters
        ----------
        value : X | str
            The value to strip, if needed.

        Returns
        -------
        X | str
            The value, possibly strippped.
        """
        if isinstance(value, str):
            return value.strip()
        return value
