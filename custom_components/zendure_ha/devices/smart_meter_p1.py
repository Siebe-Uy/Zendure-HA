"""Zendure Smart Meter P1 and related grid meter devices."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..device import CONST_HEADER, CONST_TIMEOUT, ZendureDevice
from ..entity import EntityDevice, snakecase
from ..sensor import ZendureSensor

_LOGGER = logging.getLogger(__name__)

# Keys skipped when applying a local HTTP /properties/report payload.
_HTTP_META_KEYS = frozenset({"timestamp", "messageId", "deviceId"})

# Sensor keys tried in order for Zendure Manager grid-power input.
PRIMARY_POWER_KEYS = (
    "total_power",
    "gridPower",
    "gridInputPower",
    "energyPower",
    "power",
    "totalPower",
    "activePower",
    "importPower",
)


class ZendureMeter(ZendureDevice):
    """Read-only Zendure grid / P1 meter (local HTTP and/or cloud MQTT)."""

    def __init__(self, hass: HomeAssistant, deviceId: str, prodName: str, definition: Any) -> None:
        """Initialize Smart Meter P1."""
        super().__init__(hass, deviceId, prodName, definition["productModel"], definition)
        self.session = async_get_clientsession(hass, verify_ssl=False)
        self.setLimits(0, 0)

    def _uses_local_http(self) -> bool:
        """True when a fixed host/IP was configured (not mDNS placeholder only)."""
        ip = self.ipAddress or ""
        return ip != "" and not ip.startswith("zendure-")

    def create_entities(self) -> None:
        """Create minimal entities; other keys are created dynamically from telemetry."""
        self.connectionStatus = ZendureSensor(self, "connectionStatus")
        self.totalPower = ZendureSensor(self, "total_power", None, "W", "power", "measurement")
        self.gridPower = ZendureSensor(self, "gridPower", None, "W", "power", "measurement")
        self.phaseAPower = ZendureSensor(self, "a_aprt_power", None, "W", "power", "measurement")
        self.phaseBPower = ZendureSensor(self, "b_aprt_power", None, "W", "power", "measurement")
        self.phaseCPower = ZendureSensor(self, "c_aprt_power", None, "W", "power", "measurement")

    def setStatus(self) -> None:
        """Update connection status from last successful poll."""
        if self.lastseen == datetime.min:
            self.connectionStatus.update_value(0)
        elif self._uses_local_http():
            self.connectionStatus.update_value(12)
        else:
            self.connectionStatus.update_value(10)

    async def httpGet(self, path: str) -> dict[str, Any]:
        """GET local zenSDK-style /properties/report."""
        try:
            url = f"http://{self.ipAddress}/{path}"
            response = await self.session.get(url, headers=CONST_HEADER, timeout=CONST_TIMEOUT)
            payload = json.loads(await response.text())
            if isinstance(payload, dict):
                self.lastseen = datetime.now()
                return payload
        except Exception as e:
            _LOGGER.error("%s for %s during httpGet: %s", type(e).__name__, self.name, e)
            self.lastseen = datetime.min
        return {}

    async def httpProperties(self, payload: dict[str, Any]) -> None:
        """Apply flat HTTP report fields (not wrapped in a properties object)."""
        if not payload:
            return

        for key, value in payload.items():
            if key in _HTTP_META_KEYS:
                continue
            self.entityUpdate(key, value)

        if (total := payload.get("total_power")) is not None:
            self.entityUpdate("gridPower", total)

        self.setStatus()

    async def dataRefresh(self, _update_count: int) -> None:
        """Poll local HTTP or request cloud MQTT properties."""
        if self._uses_local_http():
            await self.httpProperties(await self.httpGet("properties/report"))
            return

        from ..api import Api

        mqtt_payload = {"properties": ["getAll"]}
        if self.lastseen != datetime.min:
            self.mqttPublish(self.topic_read, mqtt_payload, self.mqtt)
        else:
            self.mqttPublish(self.topic_read, mqtt_payload, Api.mqttCloud)

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
        for key in PRIMARY_POWER_KEYS:
            entity_id = f"sensor.{snakecase(self.name.lower())}_{snakecase(key)}"
            if self.hass is None or self.hass.states.get(entity_id) is not None:
                return entity_id
        return f"sensor.{snakecase(self.name.lower())}_total_power"

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
        """Handle cloud MQTT payloads (properties object) or flat HTTP-style bodies."""
        if isinstance(payload, dict) and "properties" not in payload and "total_power" in payload:
            await self.httpProperties(payload)
            return
        await super().mqttProperties(payload)
        self.setStatus()
