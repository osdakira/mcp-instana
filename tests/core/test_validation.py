"""
Tests for Validation Module

This module contains comprehensive tests for the validation utility functions.
"""

import unittest
from datetime import datetime
from unittest.mock import patch

from src.core.validation import (
    EventsValidator,
    TimeValidator,
    ValidationError,
    ValidationResult,
)


class TestValidationError(unittest.TestCase):
    """Test ValidationError class"""

    def test_validation_error_basic(self):
        """Test basic ValidationError creation"""
        error = ValidationError(
            field="test_field",
            message="Test error message"
        )
        self.assertEqual(error.field, "test_field")
        self.assertEqual(error.message, "Test error message")
        self.assertIsNone(error.provided_value)
        self.assertIsNone(error.valid_values)
        self.assertIsNone(error.valid_range)
        self.assertIsNone(error.example)

    def test_validation_error_with_all_fields(self):
        """Test ValidationError with all optional fields"""
        error = ValidationError(
            field="test_field",
            message="Test error",
            provided_value="invalid",
            valid_values=["valid1", "valid2"],
            valid_range="1-100",
            example="valid1"
        )
        self.assertEqual(error.provided_value, "invalid")
        self.assertEqual(error.valid_values, ["valid1", "valid2"])
        self.assertEqual(error.valid_range, "1-100")
        self.assertEqual(error.example, "valid1")

    def test_validation_error_to_dict_basic(self):
        """Test to_dict with basic fields only"""
        error = ValidationError(
            field="test_field",
            message="Test error"
        )
        result = error.to_dict()
        self.assertEqual(result["field"], "test_field")
        self.assertEqual(result["message"], "Test error")
        self.assertNotIn("provided_value", result)
        self.assertNotIn("valid_values", result)
        self.assertNotIn("valid_range", result)
        self.assertNotIn("example", result)

    def test_validation_error_to_dict_with_all_fields(self):
        """Test to_dict with all fields"""
        error = ValidationError(
            field="test_field",
            message="Test error",
            provided_value="invalid",
            valid_values=["valid1", "valid2"],
            valid_range="1-100",
            example="valid1"
        )
        result = error.to_dict()
        self.assertEqual(result["field"], "test_field")
        self.assertEqual(result["message"], "Test error")
        self.assertEqual(result["provided_value"], "invalid")
        self.assertEqual(result["valid_values"], ["valid1", "valid2"])
        self.assertEqual(result["valid_range"], "1-100")
        self.assertEqual(result["example"], "valid1")

    def test_validation_error_to_dict_with_zero_value(self):
        """Test to_dict with provided_value of 0 (falsy but not None)"""
        error = ValidationError(
            field="test_field",
            message="Test error",
            provided_value=0
        )
        result = error.to_dict()
        self.assertIn("provided_value", result)
        self.assertEqual(result["provided_value"], 0)


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult class"""

    def test_validation_result_init(self):
        """Test ValidationResult initialization"""
        result = ValidationResult()
        self.assertEqual(len(result.errors), 0)
        self.assertTrue(result.is_valid())

    def test_validation_result_add_error(self):
        """Test adding errors to ValidationResult"""
        result = ValidationResult()
        error = ValidationError(field="test", message="error")
        result.add_error(error)
        self.assertEqual(len(result.errors), 1)
        self.assertFalse(result.is_valid())

    def test_validation_result_multiple_errors(self):
        """Test adding multiple errors"""
        result = ValidationResult()
        result.add_error(ValidationError(field="field1", message="error1"))
        result.add_error(ValidationError(field="field2", message="error2"))
        self.assertEqual(len(result.errors), 2)
        self.assertFalse(result.is_valid())

    def test_validation_result_to_dict_valid(self):
        """Test to_dict when validation is valid"""
        result = ValidationResult()
        result_dict = result.to_dict()
        self.assertEqual(result_dict, {"valid": True})

    def test_validation_result_to_dict_invalid(self):
        """Test to_dict when validation has errors"""
        result = ValidationResult()
        result.add_error(ValidationError(field="test", message="error"))
        result_dict = result.to_dict()
        self.assertFalse(result_dict["valid"])
        self.assertEqual(result_dict["error_count"], 1)
        self.assertIn("errors", result_dict)
        self.assertIn("message", result_dict)
        self.assertEqual(len(result_dict["errors"]), 1)


class TestTimeValidator(unittest.TestCase):
    """Test TimeValidator class"""

    def test_validate_timestamp_none_not_required(self):
        """Test timestamp validation with None when not required"""
        error = TimeValidator.validate_timestamp(None, "test_field", required=False)
        self.assertIsNone(error)

    def test_validate_timestamp_none_required(self):
        """Test timestamp validation with None when required"""
        error = TimeValidator.validate_timestamp(None, "test_field", required=True)
        self.assertIsNotNone(error)
        self.assertEqual(error.field, "test_field")
        self.assertIn("required", error.message)

    def test_validate_timestamp_invalid_type(self):
        """Test timestamp validation with invalid type"""
        error = TimeValidator.validate_timestamp("not_an_int", "test_field")
        self.assertIsNotNone(error)
        self.assertIn("must be an integer", error.message)

    def test_validate_timestamp_too_old(self):
        """Test timestamp validation with timestamp before Jan 1, 2020"""
        old_timestamp = 1000000000000  # Year 2001
        error = TimeValidator.validate_timestamp(old_timestamp, "test_field")
        self.assertIsNotNone(error)
        self.assertIn("too far in the past", error.message)

    @patch('src.core.validation.datetime')
    def test_validate_timestamp_in_future(self, mock_datetime):
        """Test timestamp validation with future timestamp"""
        # Mock current time
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        future_timestamp = current_time_ms + 120000  # 2 minutes in future

        error = TimeValidator.validate_timestamp(future_timestamp, "test_field")
        self.assertIsNotNone(error)
        self.assertIn("cannot be in the future", error.message)

    @patch('src.core.validation.datetime')
    def test_validate_timestamp_valid(self, mock_datetime):
        """Test timestamp validation with valid timestamp"""
        # Mock current time
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        valid_timestamp = current_time_ms - 86400000  # Yesterday

        error = TimeValidator.validate_timestamp(valid_timestamp, "test_field")
        self.assertIsNone(error)

    @patch('src.core.validation.datetime')
    def test_validate_timestamp_with_clock_skew(self, mock_datetime):
        """Test timestamp validation allows 1 minute clock skew"""
        # Mock current time
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        # 30 seconds in future (within 1 minute skew allowance)
        timestamp_with_skew = current_time_ms + 30000

        error = TimeValidator.validate_timestamp(timestamp_with_skew, "test_field")
        self.assertIsNone(error)

    def test_validate_time_range_none(self):
        """Test time range validation with None"""
        error = TimeValidator.validate_time_range(None)
        self.assertIsNone(error)

    def test_validate_time_range_invalid_type(self):
        """Test time range validation with invalid type"""
        error = TimeValidator.validate_time_range(123)
        self.assertIsNotNone(error)
        self.assertIn("must be a string", error.message)

    def test_validate_time_range_valid_minutes(self):
        """Test time range validation with valid minutes"""
        error = TimeValidator.validate_time_range("last 30 minutes")
        self.assertIsNone(error)

    def test_validate_time_range_valid_hours(self):
        """Test time range validation with valid hours"""
        error = TimeValidator.validate_time_range("last 24 hours")
        self.assertIsNone(error)

    def test_validate_time_range_valid_days(self):
        """Test time range validation with valid days"""
        error = TimeValidator.validate_time_range("last 7 days")
        self.assertIsNone(error)

    def test_validate_time_range_valid_weeks(self):
        """Test time range validation with valid weeks"""
        error = TimeValidator.validate_time_range("last 2 weeks")
        self.assertIsNone(error)

    def test_validate_time_range_valid_months(self):
        """Test time range validation with valid months"""
        error = TimeValidator.validate_time_range("last 1 month")
        self.assertIsNone(error)

    def test_validate_time_range_valid_few_hours(self):
        """Test time range validation with 'last few hours'"""
        error = TimeValidator.validate_time_range("last few hours")
        self.assertIsNone(error)

    def test_validate_time_range_case_insensitive(self):
        """Test time range validation is case insensitive"""
        error = TimeValidator.validate_time_range("LAST 24 HOURS")
        self.assertIsNone(error)

    def test_validate_time_range_invalid_format(self):
        """Test time range validation with invalid format"""
        error = TimeValidator.validate_time_range("invalid format")
        self.assertIsNotNone(error)
        self.assertIn("not recognized", error.message)

    def test_validate_time_range_too_many_minutes(self):
        """Test time range validation with too many minutes"""
        error = TimeValidator.validate_time_range("last 2000 minutes")
        self.assertIsNotNone(error)
        self.assertIn("too many minutes", error.message)

    def test_validate_time_range_too_many_hours(self):
        """Test time range validation with too many hours"""
        error = TimeValidator.validate_time_range("last 1000 hours")
        self.assertIsNotNone(error)
        self.assertIn("too many hours", error.message)

    def test_validate_time_range_too_many_days(self):
        """Test time range validation with too many days"""
        error = TimeValidator.validate_time_range("last 100 days")
        self.assertIsNotNone(error)
        self.assertIn("too many days", error.message)

    def test_validate_time_range_too_many_weeks(self):
        """Test time range validation with too many weeks"""
        error = TimeValidator.validate_time_range("last 15 weeks")
        self.assertIsNotNone(error)
        self.assertIn("too many weeks", error.message)

    def test_validate_time_range_too_many_months(self):
        """Test time range validation with too many months"""
        error = TimeValidator.validate_time_range("last 5 months")
        self.assertIsNotNone(error)
        self.assertIn("too many months", error.message)

    def test_validate_time_range_singular_forms(self):
        """Test time range validation with singular forms"""
        self.assertIsNone(TimeValidator.validate_time_range("last 1 minute"))
        self.assertIsNone(TimeValidator.validate_time_range("last 1 hour"))
        self.assertIsNone(TimeValidator.validate_time_range("last 1 day"))
        self.assertIsNone(TimeValidator.validate_time_range("last 1 week"))
        self.assertIsNone(TimeValidator.validate_time_range("last 1 month"))

    def test_validate_time_parameters_no_params(self):
        """Test time parameters validation with no parameters"""
        result = TimeValidator.validate_time_parameters()
        self.assertFalse(result.is_valid())
        self.assertEqual(len(result.errors), 1)
        self.assertIn("MISSING REQUIRED PARAMETER", result.errors[0].message)

    def test_validate_time_parameters_with_time_range(self):
        """Test time parameters validation with time_range"""
        result = TimeValidator.validate_time_parameters(time_range="last 24 hours")
        self.assertTrue(result.is_valid())

    @patch('src.core.validation.datetime')
    def test_validate_time_parameters_with_from_time(self, mock_datetime):
        """Test time parameters validation with from_time"""
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        from_time = current_time_ms - 86400000  # Yesterday

        result = TimeValidator.validate_time_parameters(from_time=from_time)
        self.assertTrue(result.is_valid())

    @patch('src.core.validation.datetime')
    def test_validate_time_parameters_with_both_timestamps(self, mock_datetime):
        """Test time parameters validation with both timestamps"""
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        from_time = current_time_ms - 86400000  # Yesterday
        to_time = current_time_ms

        result = TimeValidator.validate_time_parameters(from_time=from_time, to_time=to_time)
        self.assertTrue(result.is_valid())

    @patch('src.core.validation.datetime')
    def test_validate_time_parameters_from_after_to(self, mock_datetime):
        """Test time parameters validation when from_time is after to_time"""
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        from_time = current_time_ms
        to_time = current_time_ms - 86400000  # Yesterday

        result = TimeValidator.validate_time_parameters(from_time=from_time, to_time=to_time)
        self.assertFalse(result.is_valid())
        self.assertTrue(any("must be before" in error.message for error in result.errors))

    @patch('src.core.validation.datetime')
    def test_validate_time_parameters_range_too_large(self, mock_datetime):
        """Test time parameters validation with range exceeding 90 days"""
        mock_now = datetime(2026, 4, 8, 5, 0, 0)
        mock_datetime.now.return_value = mock_now

        current_time_ms = int(mock_now.timestamp() * 1000)
        from_time = current_time_ms - (100 * 24 * 60 * 60 * 1000)  # 100 days ago
        to_time = current_time_ms

        result = TimeValidator.validate_time_parameters(from_time=from_time, to_time=to_time)
        self.assertFalse(result.is_valid())
        self.assertTrue(any("too large" in error.message for error in result.errors))

    def test_validate_time_parameters_invalid_time_range(self):
        """Test time parameters validation with invalid time_range"""
        result = TimeValidator.validate_time_parameters(time_range="invalid")
        self.assertFalse(result.is_valid())

    def test_validate_time_parameters_invalid_from_time(self):
        """Test time parameters validation with invalid from_time"""
        result = TimeValidator.validate_time_parameters(from_time="not_an_int")
        self.assertFalse(result.is_valid())


class TestEventsValidator(unittest.TestCase):
    """Test EventsValidator class"""

    def test_validate_event_type_filters_none(self):
        """Test event type filters validation with None"""
        error = EventsValidator.validate_event_type_filters(None)
        self.assertIsNone(error)

    def test_validate_event_type_filters_invalid_type(self):
        """Test event type filters validation with invalid type"""
        error = EventsValidator.validate_event_type_filters("not_a_list")
        self.assertIsNotNone(error)
        self.assertIn("must be a list", error.message)

    def test_validate_event_type_filters_valid_single(self):
        """Test event type filters validation with single valid type"""
        error = EventsValidator.validate_event_type_filters(["incident"])
        self.assertIsNone(error)

    def test_validate_event_type_filters_valid_multiple(self):
        """Test event type filters validation with multiple valid types"""
        error = EventsValidator.validate_event_type_filters(["incident", "issue", "change"])
        self.assertIsNone(error)

    def test_validate_event_type_filters_invalid_type_in_list(self):
        """Test event type filters validation with invalid type in list"""
        error = EventsValidator.validate_event_type_filters(["incident", "invalid_type"])
        self.assertIsNotNone(error)
        self.assertIn("Invalid event types", error.message)
        self.assertIn("invalid_type", error.message)

    def test_validate_event_type_filters_all_invalid(self):
        """Test event type filters validation with all invalid types"""
        error = EventsValidator.validate_event_type_filters(["invalid1", "invalid2"])
        self.assertIsNotNone(error)
        self.assertIn("invalid1", error.message)
        self.assertIn("invalid2", error.message)

    def test_validate_event_type_filters_empty_list(self):
        """Test event type filters validation with empty list"""
        error = EventsValidator.validate_event_type_filters([])
        self.assertIsNone(error)

    def test_validate_max_events_none(self):
        """Test max_events validation with None"""
        error = EventsValidator.validate_max_events(None)
        self.assertIsNone(error)

    def test_validate_max_events_invalid_type(self):
        """Test max_events validation with invalid type"""
        error = EventsValidator.validate_max_events("not_an_int")
        self.assertIsNotNone(error)
        self.assertIn("must be an integer", error.message)

    def test_validate_max_events_too_small(self):
        """Test max_events validation with value less than 1"""
        error = EventsValidator.validate_max_events(0)
        self.assertIsNotNone(error)
        self.assertIn("must be at least 1", error.message)

    def test_validate_max_events_negative(self):
        """Test max_events validation with negative value"""
        error = EventsValidator.validate_max_events(-5)
        self.assertIsNotNone(error)
        self.assertIn("must be at least 1", error.message)

    def test_validate_max_events_too_large(self):
        """Test max_events validation with value greater than 1000"""
        error = EventsValidator.validate_max_events(1500)
        self.assertIsNotNone(error)
        self.assertIn("too large", error.message)

    def test_validate_max_events_valid_min(self):
        """Test max_events validation with minimum valid value"""
        error = EventsValidator.validate_max_events(1)
        self.assertIsNone(error)

    def test_validate_max_events_valid_max(self):
        """Test max_events validation with maximum valid value"""
        error = EventsValidator.validate_max_events(1000)
        self.assertIsNone(error)

    def test_validate_max_events_valid_middle(self):
        """Test max_events validation with middle range value"""
        error = EventsValidator.validate_max_events(50)
        self.assertIsNone(error)


class TestValidatorConstants(unittest.TestCase):
    """Test validator constants"""

    def test_time_validator_max_time_range(self):
        """Test TimeValidator MAX_TIME_RANGE_MS constant"""
        expected = 90 * 24 * 60 * 60 * 1000  # 90 days in milliseconds
        self.assertEqual(TimeValidator.MAX_TIME_RANGE_MS, expected)

    def test_time_validator_min_timestamp(self):
        """Test TimeValidator MIN_TIMESTAMP_MS constant"""
        expected = 1577836800000  # Jan 1, 2020
        self.assertEqual(TimeValidator.MIN_TIMESTAMP_MS, expected)

    def test_events_validator_valid_event_types(self):
        """Test EventsValidator VALID_EVENT_TYPES constant"""
        expected = ["incident", "issue", "change"]
        self.assertEqual(EventsValidator.VALID_EVENT_TYPES, expected)


if __name__ == '__main__':
    unittest.main()

