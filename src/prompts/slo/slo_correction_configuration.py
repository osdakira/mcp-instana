from typing import Optional

from src.prompts import auto_register_prompt


class SLOCorrectionPrompts:
    """Class containing SLO correction window configuration related prompts"""

    @auto_register_prompt
    @staticmethod
    def get_all_corrections(
        page_size: Optional[int] = None,
        page: Optional[int] = None,
        order_by: Optional[str] = None,
        order_direction: Optional[str] = None,
        query: Optional[str] = None,
        tag: Optional[list] = None,
        id: Optional[list] = None,
        slo_id: Optional[list] = None,
        refresh: Optional[bool] = None,
    ) -> str:
        """Get all SLO correction window configurations with optional filtering"""
        return f"""
        Get all SLO correction windows:
        - Page size: {page_size or 'default'}
        - Page: {page or '1'}
        - Order by: {order_by or 'None'}
        - Order direction: {order_direction or 'None'}
        - Query: {query or 'None'}
        - Tags: {tag or 'None'}
        - IDs: {id or 'None'}
        - SLO IDs: {slo_id or 'None'}
        - Refresh: {refresh or 'False'}
        """

    @auto_register_prompt
    @staticmethod
    def get_correction_by_id(id: str) -> str:
        """Get a specific SLO correction window configuration by ID"""
        return f"""
        Get SLO correction window:
        - ID: {id}
        """

    @auto_register_prompt
    @staticmethod
    def create_correction(
        name: str,
        scheduling: dict,
        slo_ids: Optional[list] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        active: Optional[bool] = None,
    ) -> str:
        """Create new SLO correction window configuration"""
        return f"""
        Create SLO correction window:
        - Name: {name}
        - Scheduling: {scheduling}
        - SLO IDs: {slo_ids or 'None'}
        - Description: {description or 'None'}
        - Tags: {tags or 'None'}
        - Active: {active or 'True'}
        """

    @auto_register_prompt
    @staticmethod
    def update_correction(
        id: str,
        name: str,
        scheduling: dict,
        slo_ids: Optional[list] = None,
        description: Optional[str] = None,
        tags: Optional[list] = None,
        active: Optional[bool] = None,
    ) -> str:
        """Update existing SLO correction window configuration"""
        return f"""
        Update SLO correction window:
        - ID: {id}
        - Name: {name}
        - Scheduling: {scheduling}
        - SLO IDs: {slo_ids or 'None'}
        - Description: {description or 'None'}
        - Tags: {tags or 'None'}
        - Active: {active or 'True'}
        """

    @auto_register_prompt
    @staticmethod
    def delete_correction(id: str) -> str:
        """Delete SLO correction window configuration"""
        return f"""
        Delete SLO correction window:
        - ID: {id}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('get_all_corrections', cls.get_all_corrections),
            ('get_correction_by_id', cls.get_correction_by_id),
            ('create_correction', cls.create_correction),
            ('update_correction', cls.update_correction),
            ('delete_correction', cls.delete_correction),
        ]
