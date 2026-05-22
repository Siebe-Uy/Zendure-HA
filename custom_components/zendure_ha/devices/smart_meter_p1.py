"""Zendure Smart Meter P1 and related grid meter devices."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant

from ..device import ZendureDevice
from ..entity import EntityDevice, snakecase
from ..sensor import ZendureSensor

_LOGGER = logging.getLogger(__name__)

# MQTT property keys tried in order for Zendure Manager grid-power input.
PRIMARY_POWER_KEYS = (
    "gridPower",
    "gridInputPower",
    "energyPower",
    "power",
    "totalPower",
    "activePower",
    "importPower",
)


class ZendureMeter(ZendureDevice):
    """Read-only Zendure grid / P1 meter (no battery or Manager power control)."""

    def __init__(self, hass: HomeAssistant, deviceId: str, prodName: str, definition: Any) -> None:
        """Initialize Smart Meter P1."""
        super().__init__(hass, deviceId, prodName, definition["productModel"], definition)
        self.setLimits(0, 0)

    def create_entities(self) -> None:
        """Create minimal entities; other keys are created dynamically from MQTT."""
        self.connectionStatus = ZendureSensor(self, "connectionStatus")
        self.gridPower = ZendureSensor(self, "gridPower", None, "W", "power", "measurement")

    def setStatus(self) -> None:
        """Update connection status from last MQTT activity."""
        if self.lastseen == datetime.min:
            self.connectionStatus.update_value(0)
        else:
            self.connectionStatus.update_value(10)

    async def dataRefresh(self, _update_count: int) -> None:
        """Request a full property report from the cloud broker."""
        from ..api import Api

        payload = {"properties": ["getAll"]}
        if self.lastseen != datetime.min:
            self.mqttPublish(self.topic_read, payload, self.mqtt)
        else:
            self.mqttPublish(self.topic_read, payload, Api.mqttCloud)

    async def power_get(self) -> bool:
        """Meters are not controlled by Zendure Manager."""
        return False

    async def charge(self, _power: int) -> int:
        return 0

    async def discharge(self, _power: int) -> int:
        return 0

    async def power_off(self) -> None:
        return

    async def power_charge(self, power: int) -> int:
        return 0

    async def power_discharge(self, power: int) -> int:
        return 0

    @property
    def suggested_p1_entity_id(self) -> str:
        """Entity id used by Zendure Manager for this meter's grid power."""
        entity_id = self._entity_id_for_key("grid_power")
        if entity_id is not None:
            return entity_id
        for key in PRIMARY_POWER_KEYS:
            if (entity_id := self._entity_id_for_key(snakecase(key))) is not None:
                return entity_id
        return f"sensor.{snakecase(self.name.lower())}_grid_power"

    def _entity_id_for_key(self, translation_key: str) -> str | None:
        """Resolve sensor entity_id for a translation key if the entity exists."""
        for entity in self.entities.values():
            if entity is None or entity.translation_key != translation_key:
                continue
            if entity.platform is not None:
                return f"sensor.{snakecase(self.name.lower())}_{translation_key}"
        return f"sensor.{snakecase(self.name.lower())}_{translation_key}"

    def manager_power_entity_id(self) -> str | None:
        """Return the best available grid-power sensor entity_id for Manager."""
        if self.hass is None:
            return self.suggested_p1_entity_id
        for key in PRIMARY_POWER_KEYS:
            entity_id = f"sensor.{snakecase(self.name.lower())}_{snakecase(key)}"
            if self.hass.states.get(entity_id) is not None:
                return entity_id
        return self.suggested_p1_entity_id

    def entityUpdate(self, key: Any, value: Any) -> bool:
        """Update entities without battery-specific aggregation."""
        changed = EntityDevice.entityUpdate(self, key, value)
        if changed:
            self.setStatus()
        return changed

    async def mqttProperties(self, payload: Any) -> None:
        """Extend property handling to refresh connection status."""
        await super().mqttProperties(payload)
        self.setStatus()
