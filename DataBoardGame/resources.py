"""
Resource management module with classes and functions for handling different resources,
resource conversion, and scaling.
"""

from enum import IntEnum
from dataclasses import dataclass, asdict
from typing import Type

# Define an enumeration for ResourceType with specific resource types and starting index 0
ResourceType = IntEnum('ResourceType', 'rawdata datamart dashboard insight money', start=0)


@dataclass
class Resources:
    """Class representing different types of resources."""

    raw_data: int = 0
    marts: int = 0
    dashboards: int = 0
    insights: int = 0
    money: int = 0

    def __hash__(self):
        """Generate a hash based on the resource values."""
        return hash((self.raw_data, self.marts, self.dashboards, self.insights, self.money))

    def __add__(self, other):
        """Add corresponding resource values."""
        if not isinstance(other, Resources):
            return NotImplemented
        return Resources(
            raw_data=self.raw_data + other.raw_data,
            marts=self.marts + other.marts,
            dashboards=self.dashboards + other.dashboards,
            insights=self.insights + other.insights,
            money=self.money + other.money,
        )

    def __sub__(self, other):
        """Subtract corresponding resource values."""
        if not isinstance(other, Resources):
            return NotImplemented
        return Resources(
            raw_data=self.raw_data - other.raw_data,
            marts=self.marts - other.marts,
            dashboards=self.dashboards - other.dashboards,
            insights=self.insights - other.insights,
            money=self.money - other.money,
        )

    def __iadd__(self, other):
        """In-place addition of corresponding resource values."""
        if not isinstance(other, Resources):
            return NotImplemented
        self.raw_data += other.raw_data
        self.marts += other.marts
        self.dashboards += other.dashboards
        self.insights += other.insights
        self.money += other.money
        return self

    def __isub__(self, other):
        """In-place subtraction of corresponding resource values."""
        if not isinstance(other, Resources):
            return NotImplemented
        self.raw_data -= other.raw_data
        self.marts -= other.marts
        self.dashboards -= other.dashboards
        self.insights -= other.insights
        self.money -= other.money
        return self

    def __getitem__(self, res):
        """Get resource value based on ResourceType."""
        if isinstance(res, int):
            res = ResourceType(res)
        if res == ResourceType.dashboard:
            return self.dashboards
        if res == ResourceType.datamart:
            return self.marts
        if res == ResourceType.rawdata:
            return self.raw_data
        if res == ResourceType.money:
            return self.money
        if res == ResourceType.insight:
            return self.insights

    def __setitem__(self, key, value):
        """Set resource value based on ResourceType."""
        if isinstance(key, int):
            key = ResourceType(key)
        if key == ResourceType.dashboard:
            self.dashboards = value
        if key == ResourceType.datamart:
            self.marts = value
        if key == ResourceType.rawdata:
            self.raw_data = value
        if key == ResourceType.money:
            self.money = value
        if key == ResourceType.insight:
            self.insights = value

    def __lt__(self, other):
        """Compare if all resource values are less than the other Resources."""
        if not isinstance(other, Resources):
            return NotImplemented
        return (
            self.raw_data < other.raw_data
            and self.dashboards < other.dashboards
            and self.insights < other.insights
            and self.money < other.money
            and self.marts < other.marts
        )

    def __le__(self, other):
        """Compare if all resource values are less than or equal to the other Resources."""
        if not isinstance(other, Resources):
            return NotImplemented
        return (
            self.raw_data <= other.raw_data
            and self.dashboards <= other.dashboards
            and self.insights <= other.insights
            and self.money <= other.money
            and self.marts <= other.marts
        )

    def __gt__(self, other):
        """Compare if all resource values are greater than the other Resources."""
        if not isinstance(other, Resources):
            return NotImplemented
        return (
            self.raw_data > other.raw_data
            and self.dashboards > other.dashboards
            and self.insights > other.insights
            and self.money > other.money
            and self.marts > other.marts
        )

    def __ge__(self, other):
        """Compare if all resource values are greater than or equal to the other Resources."""
        if not isinstance(other, Resources):
            return NotImplemented
        return (
            self.raw_data >= other.raw_data
            and self.dashboards >= other.dashboards
            and self.insights >= other.insights
            and self.money >= other.money
            and self.marts >= other.marts
        )

    def __eq__(self, other):
        """Compare if all resource values are equal to the other Resources."""
        if not isinstance(other, Resources):
            return NotImplemented
        return (
            self.raw_data == other.raw_data
            and self.marts == other.marts
            and self.dashboards == other.dashboards
            and self.insights == other.insights
            and self.money == other.money
        )

    def apply_resource_conversion(self, resource_conversion: 'ResourceConvertion'):
        """Apply resource conversion by subtracting and adding resources."""
        self -= resource_conversion.resources_to_take
        self += resource_conversion.resource_to_give

    def apply_resource_scale(self, resource_scale: 'ResourceScale'):
        """Apply resource scaling based on specified scale."""
        mult = int(self[resource_scale.resources_to_scale_from] * resource_scale.scale)
        self[resource_scale.resource_to_scale] += mult

    def check_pay_aval(self, resource_conversion: 'ResourceConvertion'):
        """Check if resources are available to cover the conversion."""
        return self >= resource_conversion.resources_to_take

    def to_dict(self):
        """Convert Resources object to dictionary."""
        return asdict(self)


@dataclass
class ResourceConvertion:
    """Class representing the conversion between different resources."""

    resources_to_take: Resources = Resources()
    resource_to_give: Resources = Resources()

    def __add__(self, other):
        """Add corresponding resources for conversion."""
        if not isinstance(other, ResourceConvertion):
            return NotImplemented
        return ResourceConvertion(
            resources_to_take=self.resources_to_take + other.resources_to_take,
            resource_to_give=self.resource_to_give + other.resource_to_give,
        )

    def __iadd__(self, other):
        """In-place addition of corresponding resources for conversion."""
        if not isinstance(other, ResourceConvertion):
            return NotImplemented
        self.resource_to_give += other.resource_to_give
        self.resources_to_take += other.resources_to_take
        return self

    def to_dict(self):
        """Convert ResourceConvertion object to dictionary."""
        return asdict(self)

    def __eq__(self, other):
        """Compare if resource conversions are equal."""
        if not isinstance(other, ResourceConvertion):
            return NotImplemented
        return self.resources_to_take == other.resources_to_take and self.resource_to_give == other.resource_to_give

    def __hash__(self):
        """Create a hash based on the resources to give and take."""
        return hash((self.resource_to_give, self.resources_to_take))


@dataclass
class ResourceScale:
    """Class representing the scaling of resources."""

    resource_to_scale: ResourceType
    scale: float
    resources_to_scale_from: ResourceType

    def to_dict(self):
        """Convert ResourceScale object to dictionary."""
        return asdict(self)

    def __eq__(self, other):
        """Compare if resource scales are equal."""
        if not isinstance(other, ResourceScale):
            return NotImplemented
        return self.resource_to_scale == other.resource_to_scale and self.resources_to_scale_from == other.resources_to_scale_from and self.scale == other.scale

    def __hash__(self):
        """Create a hash based on the resource to scale, resources to scale from, and scale factor."""
        return hash((self.resource_to_scale, self.resources_to_scale_from, self.scale))


def money_pay(amount: int):
    """Create a ResourceConvertion object representing payment with money."""
    return ResourceConvertion(resource_to_give=Resources(), resources_to_take=Resources(money=amount))


def money_gain_per_insight(scale: float):
    """Create a ResourceScale object representing gaining money per insight."""
    return ResourceScale(resources_to_scale_from=ResourceType.insight, scale=scale, resource_to_scale=ResourceType.money)
