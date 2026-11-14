# SDS100 Monitor

> **This is a macOS fork** of [jmlynchjr/SDS-MONITOR](https://github.com/jmlynchjr/SDS-MONITOR), maintained by [cinsu](https://github.com/cinsu). The macOS changes are on the `macos` branch. Tested on an Apple Silicon Mac with an **SDS150**. Please report Mac problems here, not to the original author.

Live monitoring and control of a **Uniden SDS100** scanner from a Linux PC, over the scanner's USB serial port.

It shows what the scanner is receiving, keeps a searchable reception history, records and transcribes calls, and puts the scanner's controls, menus and analysis tools on your screen. Written in Python with PyQt6, developed and used on Kubuntu.

> SDS100 Monitor is an independent project. It is not made, endorsed or supported by Uniden. Uniden and SDS100 are trademarks of Uniden America Corporation. It uses the commands in Uniden's published SDS100 Remote Command Specification.

**User manual:** [read it online](https://github.com/cinsu/SDS-MONITOR/blob/main/docs/user-manual.md).

## What it does

- **Live display:** system, department, channel, frequency, talkgroup, unit ID, signal, site and mode, with alerts on anything you choose, and phone alerts (ntfy, Pushover, Telegram or e-mail).
- **Scanner control:** virtual keypad and knob, hold, avoid, jump to number tags, scanner menus, Close Call, Discovery, Weather (with SAME group names and Weather Alert Priority) and Tone-Out modes, a command console, screen mirror, waterfall, battery, and push updates.
- **Reception history:** every transmission in daily CSV files, with search, statistics, activity charts, unit ID log, unit names and profiles, fleet maps and Search Everything.
- **Audio:** one MP3 per transmission from your PC's audio input, with metadata, and offline speech-to-text transcription (faster-whisper).
- **Analysis:** incidents with one-line headlines and timelines, daily reports (window, PDF or HTML), Activity Watch for unusual activity, the scanner's Analyze functions (site health, channel load, unknown talkgroup and unit finder), and an antenna test.
- **Ten codes:** look-up by agency and location, decoded in transcripts (ships with the APCO 1974 list; add your own lists).
- **Aircraft (ADS-B):** with readsb or dump1090 on the same PC, alerts on emergency squawks and watched aircraft, and matches callsigns heard in airband transcripts to the aircraft in range.
- **Rdio Scanner:** sends each recorded call to your Rdio Scanner server, to listen on your phone with talkgroup and unit names, at home or (through a VPN such as Tailscale) away.
- **Places and GPS:** keeps the scanner's location updated from a GPS receiver or your phone, and maps the places mentioned in transcripts (OpenStreetMap).
- **SDS-Manager link:** with [SDS-Manager](https://github.com/jmlynchjr/SDS-Manager) (a separate program for the scanner's Favorites Lists) installed, right-click a reception → **Edit in Manager…** or **Add to Favorites List in Manager…**; quick key names, number tags and scan profiles come from SDS-Manager, and a warning shows when the scanner is out of date.
- **Plasma widget:** the Scanner Information panel as a KDE Plasma 6 widget, on a panel (channel and frequency, click for the full panel) or the desktop, with Hold, Scan and Avoid buttons. The .deb installs it; add it with **Add Widgets…** → "SDS100".
- **Extras:** a USB macro keypad, themes (light, dark, night red, accent colours, text size) and a built-in update check.

## Install

On Kubuntu or another Debian/Ubuntu system with Python 3.10 or newer:

1. Download `sds100-monitor_<version>_all.deb` from the [latest release](https://github.com/jmlynchjr/SDS-MONITOR/releases/latest).
2. `sudo apt install ./sds100-monitor_<version>_all.deb`

apt installs what it needs (PyQt6 and pyserial; Qt Multimedia and ffmpeg are recommended for audio capture). Start **SDS100 Monitor** from the application menu, or run `sds100-monitor`. Remove it with `sudo apt remove sds100-monitor`; your data stays.

Connect the SDS100 by USB and choose **Serial Port** on the scanner when it asks.

Other distributions: install PyQt6 and pyserial for Python 3 and run `python3 sds100_monitor.py` from this folder (or `bash install.sh` to add a menu entry).

## Running on macOS

This fork adds macOS support. Nothing changes for Linux users.

**Requirements:** macOS on Apple Silicon or Intel, [Homebrew](https://brew.sh), and git (macOS offers to install git the first time you run it).

**1. Download and set up (one time):**

```bash
cd ~
git clone -b macos https://github.com/cinsu/SDS-MONITOR-macOS.git SDS-MONITOR
cd ~/SDS-MONITOR
./setup-mac.sh
```

`setup-mac.sh` installs Python 3.12 and ffmpeg with Homebrew and puts the Monitor's own Python packages (PyQt6, pyserial) in a private folder, `.venv-mac`. Nothing else on your Mac is changed.

**2. Connect the scanner:** plug it in by USB and choose **Serial Port** on the scanner when it asks.

**3. Start the Monitor:**

```bash
~/SDS-MONITOR/launch-mac.sh
```

Choose the port that starts with `/dev/cu.usbmodem` (it shows Uniden's USB ID, `0x1965`).

**Run the tests:**

```bash
cd ~/SDS-MONITOR && .venv-mac/bin/python -m unittest discover -s tests -t tests
```

**Get updates:**

```bash
cd ~/SDS-MONITOR && git pull
```

**Where things are kept on macOS:** settings in `~/.config/SDS100Monitor/Monitor110.conf`, and reception history, recordings and transcripts in `~/SDS100Monitor`, the same places as on Linux.

**What's different on macOS:**

- **Alerts** use macOS notifications and the system "Glass" sound.
- **USB macro keypad:** not supported. It reads Linux input devices directly.
- **Help → Check for Updates:** installs Linux `.deb` packages, so it doesn't work on a Mac. Turn the automatic check off in that window and use `git pull` instead.
- **Recording and transcription:** most current Macs have no line-in jack, so you'll need a USB audio adapter. macOS asks permission for Terminal to use the microphone the first time. Transcription runs on the CPU; leave the NVIDIA GPU option unchecked.
- **SDS150:** live display and controls work. The original program was written for the SDS100, so some SDS150 features may behave differently.

## Updates

**Help → Check for Updates…** checks this repository's latest release (and your Downloads folder), shows what's new and installs the update with one click (it asks for your password). It also checks quietly at start; you can turn that off in the same window.

## Your data

Everything the Monitor records stays on your PC, in `~/SDS100Monitor`: reception history, recordings, transcripts, unit names, reports and settings. It sends nothing anywhere except for the features you use that need the internet: phone alerts, place look-ups (OpenStreetMap), the update check (GitHub) and installing the transcription engine (downloaded once from the Python package index and Hugging Face; transcription itself runs on your PC). It never writes to the scanner's SD card.

## Testing

`bash run_tests.sh` runs the automated tests (about 100, a few seconds; add `-v` to list them). They never touch your real data, settings or scanner: every test works in its own throw-away home folder and no serial port is opened.

- Most tests run the program's logic on a stand-in for Qt, so they run anywhere, including on GitHub.
- Where PyQt6 is installed, two more start the real program on the real Qt, off screen: one triggers every menu command, opens every window and switches themes; the other starts and closes the program and fails on any crash.

## Removing old folder installs

Once the .deb is installed, every folder install in your home is an old version: `bash /opt/sds100-monitor/cleanup_old_installs.sh` lists them all (and `--delete` removes them).

`bash cleanup_old_installs.sh` lists every installed SDS100 Monitor version except the newest, with its menu launcher. It only lists; nothing is removed until you run it again with `--delete` and type the confirmation.

- To keep particular older versions as well, add `--keep`, e.g. `--keep 24` or `--keep 1.1.14` (can be repeated).
- V24 is the last version with the database/favorites panel, so the preview reminds you about `--keep 24` if it is installed.
- Reception history (`~/SDS100Monitor`), `~/SDS100MonitorData` and all CSV, HPDB and Favorites List files are never touched.

Beta Testers Wanted
If you have an SDS150 or SDS200 and would be interested in beta testing features specific to those units please contact me.

## Credits and licence

SDS100 Monitor is by J. Lynch, developed with the help of AI (Anthropic's Claude), and tested on a real SDS100.

Copyright © 2026 J. Lynch. Free software under the [GNU General Public License v3](LICENSE) or later: you may use, share and change it under its terms. It comes with **no warranty**.

See [CHANGELOG.md](CHANGELOG.md) for what changed in each version.
