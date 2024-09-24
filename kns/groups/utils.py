"""
Utility functions for the `groups` app.
"""

from django.db.models import Avg, Count
from django_countries import countries


class GroupStatistics:
    """
    A utility class to compute various statistics for groups.

    Parameters
    ----------
    groups : QuerySet
        A queryset of groups that have been filtered for the specific statistics.
    """

    def __init__(self, groups):
        """
        Initialize the GroupStatistics class with a filtered groups queryset.

        Parameters
        ----------
        groups : QuerySet
            A queryset of filtered Group objects to compute statistics on.
        """
        self.groups = groups

    def get_no_groups(self):
        """
        Get the total number of groups in the filtered queryset.

        Returns
        -------
        int
            The number of groups in the queryset.
        """
        return self.groups.count()

    def get_top_3_cities_with_most_groups(self):
        """
        Get the top 3 cities with the most groups in the queryset.

        Returns
        -------
        QuerySet
            A queryset of dictionaries containing the city and the corresponding group count,
            ordered by the city with the most groups.
        """
        return (
            self.groups.values("location_city")
            .annotate(group_count=Count("id"))
            .order_by("-group_count")[:3]
        )

    def get_top_3_countries_with_most_groups(self):
        """
        Get the top 3 countries with the most groups in the queryset.

        Returns
        -------
        QuerySet
            A queryset of dictionaries containing the country and the corresponding group count,
            ordered by the country with the most groups.
        """
        return (
            self.groups.values("location_country")
            .annotate(group_count=Count("id"))
            .order_by("-group_count")[:3]
        )

    def get_most_recent_group(self):
        """
        Get the most recently created group in the queryset.

        Returns
        -------
        Group or None
            The newest group object (based on `created_at`), or None if no groups exist.
        """
        return self.groups.order_by("-created_at").first()

    def get_group_with_most_members(self):
        """
        Get the group with the most members in the queryset.

        Returns
        -------
        Group or None
            The group object with the most members, or None if no groups exist.
        """
        return (
            self.groups.annotate(member_count=Count("members"))
            .order_by("-member_count")
            .first()
        )

    def get_avg_no_of_members_per_group(self):
        """
        Get the average number of members per group in the queryset.

        Returns
        -------
        float or None
            The average number of members per group rounded to one
            decimal point, or None if no groups exist.
        """
        avg_members = self.groups.annotate(
            member_count=Count("members"),
        ).aggregate(
            Avg("member_count")
        )["member_count__avg"]

        # Return the average rounded to one decimal place or None if avg_members is None
        return round(avg_members, 1) if avg_members is not None else None

    def get_all_statistics(self):
        """
        Return a list of dictionaries containing the label, icon, value,
        and description for each group statistic.

        Returns
        -------
        list of dict
            A list of dictionaries with 'label', 'icon', 'value', and
            'description' keys for each statistic.
        """
        stats = [
            {
                "label": "Total Groups",
                "icon": "ant-design:number-outlined",
                "value": self.get_no_groups(),
                "description": "Total number of groups.",
            },
            {
                "label": "Average Number of Members per Group",
                "icon": "icon-park-solid:people-unknown",
                "value": (
                    f"{self.get_avg_no_of_members_per_group():.1f}"
                    if self.get_avg_no_of_members_per_group() is not None
                    else "N/A"
                ),
                "description": "Average number of members across all groups.",
            },
            {
                "label": "Top 3 Countries with Most Groups",
                "icon": "subway:world",
                "value": ", ".join(
                    [
                        f"{dict(countries)[item['location_country']]} ({item['group_count']})"
                        for item in self.get_top_3_countries_with_most_groups()
                    ]
                ),
                "description": "Countries with the highest number of groups.",
            },
            {
                "label": "Top 3 Cities with Most Groups",
                "icon": "healthicons:city-outline",
                "value": ", ".join(
                    [
                        item["location_city"]
                        for item in self.get_top_3_cities_with_most_groups()
                    ]
                ),
                "description": "Cities with the highest number of groups.",
            },
            {
                "label": "Most Recent Group",
                "icon": "ic:round-fiber-new",
                "value": self.get_most_recent_group(),
                "description": "The most recently created group.",
            },
            {
                "label": "Group with Most Members",
                "icon": "ic:round-people",
                "value": self.get_group_with_most_members(),
                "description": "Group with the largest number of members.",
            },
        ]

        return stats
