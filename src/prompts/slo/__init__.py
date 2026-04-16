"""SLO prompts module."""

from src.prompts.slo.slo_alert_config import SLOAlertConfigPrompts
from src.prompts.slo.slo_configuration import SLOConfigurationPrompts
from src.prompts.slo.slo_correction_configuration import SLOCorrectionPrompts
from src.prompts.slo.slo_report import SLOReportPrompts

__all__ = [
    "SLOConfigurationPrompts",
    "SLOReportPrompts",
    "SLOAlertConfigPrompts",
    "SLOCorrectionPrompts",
]
