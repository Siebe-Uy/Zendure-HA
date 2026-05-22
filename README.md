<p align="center">
  <img src="https://zendure.com/cdn/shop/files/logo.svg" alt="Logo">
</p>

# Zendure Home Assistant Integration
This Home Assistant integration connects your Zendure devices to Home Assistant, making all reported parameters available as entities. You can track battery levels, power input/output, manage charging settings, and integrate your Zendure devices into your home automation routines. The integration also provides a power manager feature that can help balance energy usage across multiple devices when a grid-power sensor is supplied (your Zendure Smart Meter P1 or an external P1/DSMR sensor).


[![hacs][hacsbadge]][hacs] [![releasebadge]][release] [![License][license-shield]](LICENSE.md) [![hainstall][hainstallbadge]][hainstall]

## Overview

- **[Installation and ZendureApp Token](https://github.com/Zendure/Zendure-HA/wiki/Installation)**
  - [Troubleshooting Hyper2000](https://github.com/Zendure/Zendure-HA/wiki/Troubleshooting)
  - Tutorials
    - [Domotica & IoT](https://iotdomotica.nl/tutorial/install-zendure-home-assistant-integration-tutorial) 🇬🇧
    - [twoenter blog](https://www.twoenter.nl/blog/en/smarthome-en/zendure-home-battery-home-assistant-integration/) 🇬🇧 or [twoenter blog](https://www.twoenter.nl/blog/home-assistant-nl/zendure-thuisaccu-integratie-met-home-assistant/) 🇳🇱
    - [@Kieft-C](https://github.com/Kieft-C/Zendure-BKW-PV/wiki/Installation-Zendure-Home-Assistant-integration-%E2%80%93-Tutorial) 🇩🇪
  - Troubleshooting with few general hints
    - [Kieft-C](https://github.com/Kieft-C/Zendure-BKW-PV/wiki/Zendure-HA-integration-%E2%80%93-Troubleshoot-&-Mini-Anleitung) 🇩🇪

- **Configuration:**
  - [Fuse Group](https://github.com/Zendure/Zendure-HA/wiki/Fuse-Group)
  - Zendure Manager
    - [Power distribution strategy](https://github.com/Zendure/Zendure-HA/wiki/Power-distribution-strategy)
  - [Local Mqtt (Legacy devices)](https://github.com/Zendure/Zendure-HA/wiki/Local-Mqtt-(Legacy-Devices))
  - Home Assistant Energy Dashboard

- **Supported devices:**
  - Ace1500
  - Aio2400
  - Hyper2000
  - Hub1200 [German](https://github.com/Zendure/Zendure-HA/wiki/SolarFlow-Hub1200-German)
  - Hub2000
  - [SF800](https://github.com/Zendure/Zendure-HA/wiki/SolarFlow-800)
  - SF800 Pro
  - SF800 Plus
  - SF1600 AC+
  - SF2400 AC
  - SF2400 AC+
  - SF2400 Pro
  - SuperBase V6400 (?)
  - SuperBase V4600 not yet supported using the token
  - Smart Meter P1 (and SmartMeter3CT-style grid meters)

### Smart Meter P1

The **Zendure Smart Meter P1** (P1 reader + Wi‑Fi bridge) can appear as its own device in the Zendure app. Home Assistant loads it when Zendure’s HA API returns it in `deviceList`, or when **Discover meters via MQTT** is enabled and the meter publishes on the cloud broker.

- Grid power is exposed as sensors (typically `grid_power` in watts). Import is positive, export negative—matching Zendure Manager expectations.
- If you leave the Manager “grid power sensor” at the default placeholder and exactly one Zendure meter is loaded, Manager uses that meter’s `grid_power` sensor automatically.
- Otherwise pick any Home Assistant power sensor (Homewizard, DSMR, Shelly, etc.) in setup or options.

**Local HTTP (P1 bridge on your LAN):** Many P1 bridges expose data at `http://<bridge-ip>/properties/report` (zenSDK-style). In integration setup or options, set **Smart Meter P1 bridge IP or hostname** to e.g. `192.168.0.212`. The integration polls every 60s and creates sensors such as `total_power`, `a_aprt_power`, `b_aprt_power`, and `c_aprt_power` (watts; import positive).

**Troubleshooting:** After reload, check **Settings → System → Logs** for `Zendure deviceList:` lines (one per app device). If the P1 is missing there, set the bridge IP as above or enable **Log MQTT communication** and confirm `Topic: iot/…` lines for the meter. If there is no MQTT traffic and no local HTTP, the reader may only talk to your inverter over LoRa—in that case use grid-power sensors on the paired SolarFlow/Hyper device or a standalone P1 integration.

- **Device Automation:**
  - Cheap hours.

## Minimum Requirements
- [Home Assistant](https://github.com/home-assistant/core) 2025.5+

## Installation

### HACS (Home Assistant Community Store)

To install via HACS:

1. Navigate to HACS -> Integrations -> "+ Explore & Download Repos".
2. Search for "Zendure".
3. Click on the result and select "Download this Repository with HACS".
4. Refresh your browser (due to a known HA bug that may not update the integration list immediately).
5. Go to "Settings" in the Home Assistant sidebar, then select "Devices and Services".
6. Click the blue [+ Add Integration] button at the bottom right, search for "Zendure", and install it.

   [![Set up a new integration in Home Assistant](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=zendure_ha)

#### Custom repository (forks)

If you add a **custom HACS repository** (for example `https://github.com/Siebe-Uy/Zendure-HA`):

- Choose the **default branch** or a **release tag** (for example `v1.0.1`), not a raw commit hash, when HACS asks for a version.
- This integration installs from the repository tree (`zip_release` is disabled). You do **not** need a `zendure_ha.zip` release asset for HACS to work.
- Optional: push a version tag (`git tag v1.0.1 && git push origin v1.0.1`) to create a GitHub Release with `zendure_ha.zip` attached by the release workflow.


## Contributing

Contributions are welcome! If you're interested in contributing, please review our [Contribution Guidelines](CONTRIBUTING.md) before submitting a pull request or issue.

## Support

If you find this project helpful and want to support its development, consider buying me a coffee!
[![Buy Me a Coffee][buymecoffeebadge]][buymecoffee]

---

[buymecoffee]: https://www.buymeacoffee.com/fireson
[buymecoffeebadge]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
[license-shield]: https://img.shields.io/github/license/zendure/zendure-ha.svg?style=for-the-badge
[hacs]: https://github.com/zendure/zendure-ha
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[release]: https://github.com/zendure/zendure-ha/releases
[releasebadge]: https://img.shields.io/github/v/release/zendure/zendure-ha?style=for-the-badge
[buildstatus-shield]: https://img.shields.io/github/actions/workflow/status/zendure/zendure-ha/push.yml?branch=main&style=for-the-badge
[buildstatus-link]: https://github.com/zendure/zendure-ha/actions

[hainstall]: https://my.home-assistant.io/redirect/config_flow_start/?domain=zendure_ha
[hainstallbadge]: https://img.shields.io/badge/dynamic/json?style=for-the-badge&logo=home-assistant&logoColor=ccc&label=usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.zendure_ha.total


## License

MIT License
