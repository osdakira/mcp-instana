from typing import Optional

from src.prompts import auto_register_prompt


class SLOConfigurationPrompts:
    """Class containing SLO configuration related prompts"""

    @auto_register_prompt
    @staticmethod
    def get_all_slo_configs(
        page_size: Optional[int] = None,
        page: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[list] = None,
        entity_type: Optional[list] = None,
        blueprint: Optional[list] = None,
        slo_ids: Optional[list] = None,
        slo_status: Optional[str] = None,
    ) -> str:
        """Get all SLO configurations with optional filtering and pagination"""
        return f"""
        Get all SLO configurations:
        - Page size: {page_size or 'default'}
        - Page: {page or '1'}
        - Order by: {order_by or 'None'}
        - Order direction: {order_direction or 'None'}
        - Query: {query or 'None'}
        - Tags: {tag or 'None'}
        - Entity types: {entity_type or 'None'}
        - Blueprints: {blueprint or 'None'}
        - SLO IDs: {slo_ids or 'None'}
        - SLO status: {slo_status or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def get_slo_config_by_id(id: str, refresh: Optional[bool] = None) -> str:
        """Get a specific SLO configuration by ID"""
        return f"""
        Get SLO configuration:
        - ID: {id}
        - Refresh: {refresh or 'False'}
        """

    @auto_register_prompt
    @staticmethod
    def create_slo_config(
        name: str,
        entity: dict,
        indicator: dict,
        target: float,
        time_window: dict,
        tags: Optional[list] = None,
    ) -> str:
        """Create a new SLO configuration"""
        return f"""
        Create SLO configuration:
        - Name: {name}
        - Entity: {entity}
        - Indicator: {indicator}
        - Target: {target}
        - Time window: {time_window}
        - Tags: {tags or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def update_slo_config(
        id: str,
        name: str,
        entity: dict,
        indicator: dict,
        target: float,
        time_window: dict,
        tags: Optional[list] = None,
    ) -> str:
        """Update an existing SLO configuration"""
        return f"""
        Update SLO configuration:
        - ID: {id}
        - Name: {name}
        - Entity: {entity}
        - Indicator: {indicator}
        - Target: {target}
        - Time window: {time_window}
        - Tags: {tags or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def delete_slo_config(id: str) -> str:
        """Delete an SLO configuration"""
        return f"""
        Delete SLO configuration:
        - ID: {id}
        """

    @auto_register_prompt
    @staticmethod
    def get_all_slo_config_tags(
        query: Optional[str] = None,
        tag: Optional[list] = None,
        entity_type: Optional[str] = None,
    ) -> str:
        """Get all available tags for SLO configurations"""
        return f"""
        Get all SLO configuration tags:
        - Query: {query or 'None'}
        - Tags: {tag or 'None'}
        - Entity type: {entity_type or 'None'}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('get_all_slo_configs', cls.get_all_slo_configs),
            ('get_slo_config_by_id', cls.get_slo_config_by_id),
            ('create_slo_config', cls.create_slo_config),
            ('update_slo_config', cls.update_slo_config),
            ('delete_slo_config', cls.delete_slo_config),
            ('get_all_slo_config_tags', cls.get_all_slo_config_tags),
        ]
