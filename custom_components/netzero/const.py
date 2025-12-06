"""Constants for the Netzero Energy integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription, SensorStateClass
from homeassistant.const import Platform, UnitOfEnergy, UnitOfPower

DOMAIN = "netzero"
PLATFORMS = [Platform.SENSOR]

DEFAULT_UPDATE_INTERVAL = timedelta(minutes=5)
DEFAULT_BASE_URL = "https://api.netzero.energy"
DEFAULT_FLEET_BASE_URL = "https://fleet-api.prd.na.vn.cloud.tesla.com"
DEFAULT_APP_VERSION = "2.2.7"

CONF_SITE_ID = "site_id"
CONF_BEARER_TOKEN = "bearer_token"
CONF_NETZERO_TOKEN = "netzero_token"
CONF_USER_ID = "user_id"
CONF_BASE_URL = "base_url"
CONF_FLEET_BASE_URL = "fleet_base_url"
CONF_APP_VERSION = "app_version"
CONF_UPDATE_INTERVAL = "update_interval"


SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="home_total_used_kwh",
        name="Home Total Used",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="home_used_kw",
        name="Home Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="home_used_from_grid_kw",
        name="Home Power From Grid",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="home_used_from_solar_kw",
        name="Home Power From Solar",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="home_used_from_powerwall_kw",
        name="Home Power From Powerwall",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="solar_total_generated_kwh",
        name="Solar Total Generated",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="solar_generated_kw",
        name="Solar Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="grid_imported_kwh",
        name="Grid Imported",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="grid_exported_kwh",
        name="Grid Exported",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="powerwall_discharged_kwh",
        name="Powerwall Discharged",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="powerwall_charged_kwh",
        name="Powerwall Charged",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key="powerwall_discharge_kw",
        name="Powerwall Discharge Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="powerwall_charge_kw",
        name="Powerwall Charge Power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

