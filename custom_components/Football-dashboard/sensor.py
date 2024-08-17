from datetime import timedelta
import requests
import logging
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Football Fixtures'
SCAN_INTERVAL = timedelta(minutes=120)  # Set the update interval to 120 minutes

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    api_key = config.get(CONF_API_KEY)
    name = config.get(CONF_NAME)

    add_entities([FootballFixturesSensor(api_key, name)], True)

class FootballFixturesSensor(Entity):
    def __init__(self, api_key, name):
        self._api_key = api_key
        self._name = name
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def update(self):
        self._get_fixtures()

    def _get_fixtures(self):
        # Fetch fixtures for La Liga (league 140) for the 2024 season, Round 1
        url = "https://v3.football.api-sports.io/fixtures?season=2024&league=140&round=Regular Season - 1"
        headers = {
            'x-rapidapi-host': "v3.football.api-sports.io",
            'x-rapidapi-key': self._api_key
        }
        _LOGGER.debug("Fetching fixtures for La Liga Round 1 of 2024 season")
        response = requests.get(url, headers=headers)
        data = response.json()
        _LOGGER.debug("Fixtures response data: %s", data)

        if data['response']:
            fixtures = []
            for fixture in data['response']:
                home_team = fixture['teams']['home']
                away_team = fixture['teams']['away']
                match_details = {
                    'fixture_id': fixture['fixture']['id'],
                    'home_team': home_team['name'],
                    'home_team_logo': home_team['logo'],
                    'away_team': away_team['name'],
                    'away_team_logo': away_team['logo'],
                    'date': fixture['fixture']['date'],
                    'status': fixture['fixture']['status']['long'],
                    'venue': fixture['fixture']['venue']['name'],
                    'score': {
                        'halftime': fixture['score']['halftime'],
                        'fulltime': fixture['score']['fulltime']
                    }
                }
                fixtures.append(match_details)
            
            # Set the state and attributes
            self._state = f"{len(fixtures)} fixtures found"
            self._attributes['fixtures'] = fixtures
        else:
            self._state = "No fixtures found"
            self._attributes = {}
