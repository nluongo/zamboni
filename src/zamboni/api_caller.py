import requests
import logging
from typing import Union, Dict, Any

from zamboni.nhl_models import (
    GameScheduleResponse,
    PlayerResponse,
    StandingsResponse,
    RosterResponse,
)

logger = logging.getLogger(__name__)


class NHLAPIValidationError(Exception):
    """Custom exception for NHL API validation errors."""

    pass


class APICaller:
    """Class for querying the NHL API"""

    url_base = "https://api-web.nhle.com/v1/"

    def __init__(self):
        """
        Set URL variables and record type

        :param record_type: The type of record to be requested
        """
        self.url_base = APICaller.url_base
        self.url = None
        self.record_type = None

    def set_url_template(self, record_type):
        """
        Append the relevant string to the base URL based on record type

        :param record_type: The type of record to be requested
        """
        self.record_type = record_type
        if record_type == "standings":
            self.url = self.url_base + "standings/{}"
        elif record_type == "player":
            self.url = self.url_base + "player/{}/landing"
        elif record_type == "game":
            self.url = self.url_base + "schedule/{}"
        elif record_type == "roster":
            self.url = self.url_base + "roster/{}/{}{}"
        else:
            print(f"ERROR: no endpoint associated with the record type {record_type}")

    def query_url(self, record_ids, record_type=None):
        """
        Return the URL that would be queried for the given record IDs.

        :param record_ids: List of values to fill to URL
        :param record_type: Type of record being queried (game, player, standings, roster)
        :returns: Raw JSON response from NHL API
        :raises ValueError: If network error occurs
        """
        if record_type:
            self.set_url_template(record_type)
            url = self.url.format(*record_ids)
        elif self.record_type:
            url = self.url.format(*record_ids)
        else:
            ids_str = [str(record_id) for record_id in record_ids]
            url = self.url_base + "/".join(ids_str)
        return url

    def query(self, record_ids, record_type=None, throw_error=True):
        """
        Submit query to NHL API and validate response with Pydantic models.

        :param record_ids: List of values to fill to URL
        :param record_type: Type of record being queried (game, player, standings, roster)
        :param throw_error: Flag to throw error if query returns nothing
        :returns: Pydantic model instance or dict representation
        :raises NHLAPIValidationError: If API response fails Pydantic validation
        :raises ValueError: If network error occurs and throw_error is True
        """
        # if record_type:
        #    self.set_url_template(record_type)
        #    url = self.url.format(*record_ids)
        # elif self.record_type:
        #    url = self.url.format(*record_ids)
        # else:
        #    ids_str = [str(record_id) for record_id in record_ids]
        #    url = self.url_base + '/'.join(ids_str)
        url = self.query_url(record_ids, record_type=record_type)

        logger.debug(f"Attempting to query URL: {url}")
        try:
            api_out = requests.get(url)
            api_out.raise_for_status()  # Raise an HTTPError for bad responses
            json_data = api_out.json()
        except requests.exceptions.HTTPError as http_err:
            if throw_error:
                raise ValueError(f"HTTP error occurred: {http_err}") from http_err
            else:
                logger.warning(f"HTTP error occurred: {http_err}")
                return None
        except requests.exceptions.ConnectionError as conn_err:
            if throw_error:
                raise ValueError(f"Connection error occurred: {conn_err}") from conn_err
            else:
                logger.warning(f"Connection error occurred: {conn_err}")
                return None
        except requests.exceptions.Timeout as timeout_err:
            if throw_error:
                raise ValueError(
                    f"Timeout error occurred: {timeout_err}"
                ) from timeout_err
            else:
                logger.warning(f"Timeout error occurred: {timeout_err}")
                return None
        except requests.exceptions.RequestException as req_err:
            if throw_error:
                raise ValueError(f"An error occurred: {req_err}") from req_err
            else:
                logger.warning(f"An error occurred: {req_err}")
                return None
        except ValueError as json_err:
            if throw_error:
                raise ValueError(f"JSON decode error: {json_err}") from json_err
            else:
                logger.warning(f"JSON decode error: {json_err}")
                return None

        # Validate response with Pydantic model based on record type
        try:
            validated_data = self._validate_response(json_data, record_type)
            return validated_data
        except Exception as validation_err:
            if throw_error:
                raise NHLAPIValidationError(
                    f"NHL API response validation failed for {record_type}: {validation_err}"
                ) from validation_err
            else:
                logger.warning(
                    f"NHL API response validation failed for {record_type}: {validation_err}"
                )
                return None

    def _validate_response(
        self, json_data: Dict[str, Any], record_type: str
    ) -> Union[
        GameScheduleResponse,
        PlayerResponse,
        StandingsResponse,
        RosterResponse,
        Dict[str, Any],
    ]:
        """
        Validate API response JSON against appropriate Pydantic model.

        :param json_data: Raw JSON response from NHL API
        :param record_type: Type of record (game, player, standings, roster)
        :returns: Validated Pydantic model instance
        :raises ValidationError: If JSON fails Pydantic validation
        """
        if record_type == "game":
            return GameScheduleResponse(**json_data)
        elif record_type == "player":
            return PlayerResponse(**json_data)
        elif record_type == "standings":
            return StandingsResponse(**json_data)
        elif record_type == "roster":
            return RosterResponse(**json_data)
        else:
            # Return raw dict if record type is not recognized
            logger.warning(f"Unknown record type: {record_type}, returning raw JSON")
            return json_data
