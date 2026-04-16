from typing import Optional

from src.prompts import auto_register_prompt


class WebsiteAnalyzePrompts:
    """Class containing website analyze related prompts"""

    @auto_register_prompt
    @staticmethod
    def get_website_beacon_groups(payload: Optional[dict] = None, fill_time_series: Optional[bool] = None) -> str:
        """Retrieve grouped website beacon metrics for analyzing performance across dimensions like pages, browsers, or locations.

        CRITICAL: Entity field REQUIRED for ALL tag filters. ALWAYS set "entity": "NOT_APPLICABLE" for website beacon tags.
        Example: {"type": "TAG_FILTER", "name": "beacon.website.name", "operator": "EQUALS", "entity": "NOT_APPLICABLE", "value": "Robot Shop"}
        """
        return f"""
        Get website beacon groups with payload:
        - Payload: {payload if payload is not None else 'None (will use default payload)'}
        - Fill time series: {fill_time_series if fill_time_series is not None else 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def get_website_beacons(payload: Optional[dict] = None, fill_time_series: Optional[bool] = None) -> str:
        """Retrieve individual website beacon metrics with detailed beacon event information.

        CRITICAL: Entity field REQUIRED for ALL tag filters. ALWAYS set "entity": "NOT_APPLICABLE" for website beacon tags.
        Example: {"type": "TAG_FILTER", "name": "beacon.page.name", "operator": "CONTAINS", "entity": "NOT_APPLICABLE", "value": "checkout"}
        """
        return f"""
        Get website beacons with payload:
        - Payload: {payload if payload is not None else 'None (will use default payload)'}
        - Fill time series: {fill_time_series if fill_time_series is not None else 'None'}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('get_website_beacon_groups', cls.get_website_beacon_groups),
            ('get_website_beacons', cls.get_website_beacons),
        ]
