from typing import Optional

from src.prompts import auto_register_prompt


class SLOAlertConfigPrompts:
    """Class containing SLO alert configuration related prompts"""

    @auto_register_prompt
    @staticmethod
    def find_active_alert_configs(
        slo_id: Optional[str] = None,
        alert_ids: Optional[list] = None,
    ) -> str:
        """Find active SLO alert configurations"""
        return f"""
        Find active SLO alert configurations:
        - SLO ID: {slo_id or 'None'}
        - Alert IDs: {alert_ids or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def find_alert_config(id: str, valid_on: Optional[int] = None) -> str:
        """Find specific SLO alert configuration by ID"""
        return f"""
        Find SLO alert configuration:
        - ID: {id}
        - Valid on: {valid_on or 'current time'}
        """

    @auto_register_prompt
    @staticmethod
    def find_alert_config_versions(id: str) -> str:
        """Find all versions of an SLO alert configuration"""
        return f"""
        Find SLO alert configuration versions:
        - ID: {id}
        """

    @auto_register_prompt
    @staticmethod
    def create_alert_config(
        name: str,
        description: str,
        slo_ids: list,
        rule: dict,
        severity: int,
        alert_channel_ids: list,
        time_threshold: dict,
        custom_payload_fields: Optional[list] = None,
        threshold: Optional[dict] = None,
        burn_rate_time_windows: Optional[dict] = None,
    ) -> str:
        """Create new SLO alert configuration"""
        return f"""
        Create SLO alert configuration:
        - Name: {name}
        - Description: {description}
        - SLO IDs: {slo_ids}
        - Rule: {rule}
        - Severity: {severity}
        - Alert channel IDs: {alert_channel_ids}
        - Time threshold: {time_threshold}
        - Custom payload fields: {custom_payload_fields or 'None'}
        - Threshold: {threshold or 'None'}
        - Burn rate time windows: {burn_rate_time_windows or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def update_alert_config(
        id: str,
        name: str,
        description: str,
        slo_ids: list,
        rule: dict,
        severity: int,
        alert_channel_ids: list,
        time_threshold: dict,
        custom_payload_fields: Optional[list] = None,
        threshold: Optional[dict] = None,
        burn_rate_time_windows: Optional[dict] = None,
    ) -> str:
        """Update existing SLO alert configuration"""
        return f"""
        Update SLO alert configuration:
        - ID: {id}
        - Name: {name}
        - Description: {description}
        - SLO IDs: {slo_ids}
        - Rule: {rule}
        - Severity: {severity}
        - Alert channel IDs: {alert_channel_ids}
        - Time threshold: {time_threshold}
        - Custom payload fields: {custom_payload_fields or 'None'}
        - Threshold: {threshold or 'None'}
        - Burn rate time windows: {burn_rate_time_windows or 'None'}
        """

    @auto_register_prompt
    @staticmethod
    def delete_alert_config(id: str) -> str:
        """Delete SLO alert configuration"""
        return f"""
        Delete SLO alert configuration:
        - ID: {id}
        """

    @auto_register_prompt
    @staticmethod
    def disable_alert_config(id: str) -> str:
        """Disable SLO alert configuration"""
        return f"""
        Disable SLO alert configuration:
        - ID: {id}
        """

    @auto_register_prompt
    @staticmethod
    def enable_alert_config(id: str) -> str:
        """Enable SLO alert configuration"""
        return f"""
        Enable SLO alert configuration:
        - ID: {id}
        """

    @auto_register_prompt
    @staticmethod
    def restore_alert_config(id: str, created: int) -> str:
        """Restore SLO alert configuration to a specific version by creation timestamp"""
        return f"""
        Restore SLO alert configuration:
        - ID: {id}
        - Created timestamp: {created}
        """

    @classmethod
    def get_prompts(cls):
        """Return all prompts defined in this class"""
        return [
            ('find_active_alert_configs', cls.find_active_alert_configs),
            ('find_alert_config', cls.find_alert_config),
            ('find_alert_config_versions', cls.find_alert_config_versions),
            ('create_alert_config', cls.create_alert_config),
            ('update_alert_config', cls.update_alert_config),
            ('delete_alert_config', cls.delete_alert_config),
            ('disable_alert_config', cls.disable_alert_config),
            ('enable_alert_config', cls.enable_alert_config),
            ('restore_alert_config', cls.restore_alert_config),
        ]
