# Mindergas Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange)](https://hacs.xyz/)
[![version](https://img.shields.io/badge/version-v0.1.6-blue)]()

Integrate **Mindergas.nl** with Home Assistant to automatically upload your gas meter readings and retrieve your yearly prognosis.

This integration is **100% UI-based** — no YAML configuration is required.

---

## Features

- Fetch your gas meter readings automatically from Mindergas.nl
- Upload your current readings to Mindergas
- Retrieve your yearly gas usage prognosis
- Configure everything via Home Assistant UI:
    1. **API Token**
    2. **Gas meter selection**
    3. **Synchronization time**
- Cloud polling IoT class for up-to-date data

---

## Installation

### HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in Home Assistant.
2. Add this repository as a **Custom Repository** in HACS with category **Integration**.
3. Search for `Mindergas` in HACS and click **Install**.
4. Restart Home Assistant.
5. Navigate to **Configuration → Devices & Services → Add Integration → Mindergas** and follow the UI prompts.

### Manual

1. Download or clone this repository.
2. Copy the folder `mindergas` into your Home Assistant `custom_components` directory:
    ```
    config/custom_components/mindergas/
    ```
3. Restart Home Assistant.
4. Add the integration via **Configuration → Devices & Services → Add Integration → Mindergas**.

---

## Configuration (UI Only)

After adding the integration via the UI, configure the following options:

1. **API Token** – Enter your personal Mindergas API token.
2. **Gas Meter Selection** – Choose which gas meter to monitor if you have multiple.
3. **Synchronization Time** – Set the time when the readings should be fetched automatically.

> ⚠️ YAML configuration is **not supported**.

---

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## Support & Documentation

- Official Mindergas website: [https://www.mindergas.nl](https://www.mindergas.nl)
- GitHub repository: [https://github.com/nickbo90/ha-mindergas](https://github.com/nickbo90/ha-mindergas)
- For issues or feature requests, please use the GitHub Issues page.
