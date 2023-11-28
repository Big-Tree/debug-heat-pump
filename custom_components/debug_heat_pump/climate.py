""""""
from __future__ import annotations

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityDescription,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import TEMP_CELSIUS, TEMP_FAHRENHEIT

from .const import DOMAIN
from . import const
from .coordinator import DebugHeatPumpCoordinator
from .entity import DebugHeatPumpEntity

ENTITY_DESCRIPTIONS = (
    ClimateEntityDescription(
        key="debug_heat_pump",
        name="Debug Heat Pump",
        icon="mdi:heat-pump-outline",
    ),
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Set up the climate platform."""
    coordinator = hass.data[const.DOMAIN][entry.entry_id]
    async_add_devices(
        DebugHeatPumpClimate(
            coordinator=coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class DebugHeatPumpClimate(DebugHeatPumpEntity, ClimateEntity):
    """DebugHeatPumpEntity Climate class."""

    def __init__(
        self,
        coordinator: DebugHeatPumpCoordinator,
        entity_description: ClimateEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._target_temperature = 20
        self._target_temperature_high = 25
        self._target_temperature_low = 20
        match self.coordinator.config_entry.data[const.MODE]:
            case const.MODE_HEAT:
                self._hvac_mode = HVACMode.HEAT
            case const.MODE_COOL:
                self._hvac_mode = HVACMode.COOL
            case const.MODE_HEAT_COOL:
                self._hvac_mode = HVACMode.HEAT_COOL
            case _:
                raise ValueError(f'Heat_cool mode not caught: {self.coordinator.config_entry.data[const.MODE]}')

    def force_frontend_update(self):
        self.coordinator.async_set_updated_data('')

    async def async_set_hvac_mode(self, hvac_mode):
        print('----------hvac_mode set----------')
        print(hvac_mode)
        self._hvac_mode = hvac_mode
        self.force_frontend_update()
        return

    async def async_set_temperature(self, **kwargs):
        if self.supported_features & ClimateEntityFeature.TARGET_TEMPERATURE_RANGE == ClimateEntityFeature.TARGET_TEMPERATURE_RANGE:
            # kwargs has target_temp_low and target_temp_high args
            self._target_temperature_high = kwargs['target_temp_high']
            self._target_temperature_low = kwargs['target_temp_low']
            print(f'Temperature set to: \n  high: {self._target_temperature_high}\n  low: {self._target_temperature_low}')

        else:
            # kwargs has temperature arg
            self._target_temperature = kwargs['temperature']
            print(f'Temperature set to:\n  {self._target_temperature}')
        self.force_frontend_update()

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return the list of supported features."""
        #out = ClimateEntityFeature.TARGET_TEMPERATURE
        out = ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
        out |= ClimateEntityFeature.AUX_HEAT
        if self._hvac_mode == HVACMode.HEAT_COOL:
            # Do we need to include AUTO mode?
            out = ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
            out |= ClimateEntityFeature.AUX_HEAT
        else:
            out = ClimateEntityFeature.TARGET_TEMPERATURE
            out |= ClimateEntityFeature.AUX_HEAT
        return out

    @property
    def hvac_modes(self) -> HVACMode:
        match self.coordinator.config_entry.data[const.MODE]:
            case const.MODE_HEAT:
                return [
                    HVACMode.OFF,
                    HVACMode.HEAT,
                    #HVACMode.COOL,
                    #HVACMode.HEAT_COOL,
                    #HVACMode.AUTO,
                    #HVACMode.DRY,
                    HVACMode.FAN_ONLY]
            case const.MODE_COOL:
                return [
                    HVACMode.OFF,
                    #HVACMode.HEAT,
                    HVACMode.COOL,
                    #HVACMode.HEAT_COOL,
                    #HVACMode.AUTO,
                    #HVACMode.DRY,
                    HVACMode.FAN_ONLY]
            case const.MODE_HEAT_COOL:
                return [
                    HVACMode.OFF,
                    HVACMode.HEAT,
                    HVACMode.COOL,
                    HVACMode.HEAT_COOL,
                    HVACMode.AUTO,
                    HVACMode.DRY,
                    HVACMode.FAN_ONLY]
            case _:
                raise ValueError(f'Heat_cool mode not caught: {self.coordinator.config_entry.data[const.MODE]}')

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation ie. OFF, HEAT, COOL, HEAT_COOL, AUTO, DRY, FAN_ONLY.
        HEAT_COOL: The device is set to heat/cool to a target temperature range.
        AUTO: The device is set to a schedule, learned behavior, AI."""

        return self._hvac_mode

    @property
    def temperature_unit(self) -> str:
        # Our backend will always work in celsius so this should always be set to celsius.
        # The front end of homeassistant deals with unit conversion, it just needs to know which
        # units we are working with
        conversion = {
            const.TEMP_CELSIUS: TEMP_CELSIUS,
            const.TEMP_FAHRENHEIT: TEMP_FAHRENHEIT
        }
        return conversion[self.coordinator.config_entry.data[const.TEMP_UNIT]]

    @property
    def target_temperature(self) -> float:
        print(f'target_temperature:\n  {self._target_temperature}')
        return self._target_temperature

    @property
    def target_temperature_high(self) -> float:
        print(f'target_temperature_high:\n  {self._target_temperature_high}')
        return self._target_temperature_high

    @property
    def target_temperature_low(self) -> float:
        print(f'target_temperature_low:\n  {self._target_temperature_low}')
        return self._target_temperature_low

    @property
    def current_temperature(self) -> float:
        return 15

    @property
    def is_aux_heat(self) -> int:
        return None

    #@property
    #def unique_id(self):
    #    """Return a unique ID."""
    #    return 'debug_heat_pump_id'
