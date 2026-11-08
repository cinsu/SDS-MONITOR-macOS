# SDS100 Monitor — changes

Newest first. Versions before 1.1.47 were tested by hand on a real SDS100; from 1.1.47 on, every version also passes the automated tests.

## v1.1.78: Site quick keys

- **New: "Site quick key" for the Scanner Information panel** (View → Customize Scanner Information…): the quick key of the trunked site being scanned, as the scanner reports it. A site's key is one of its system's department keys (SDS-Manager 0.1.22 sets them).
- **Hold** in the panel now includes a site hold.
- Department quick key names from SDS-Manager 0.1.22 include sites, marked "(site)", in Scanner Tools → Quick Keys (no change needed here for that).
- New test checks.

## v1.1.77: Avoids in Scanner Tools

- **New: Scanner Tools → Avoids tab.** READ AVOIDS reads every system, site, department, channel and talkgroup in the scanner's Favorites Lists and shows them in one table with their avoid state (Off, Temporary in orange, Permanent in red) and where they are (list › system › department).
  - Show only avoided items, only some kinds (systems, sites, departments, channels, talkgroups), or find by name.
  - Select one or many rows (Ctrl/Shift+click) and use TEMPORARY AVOID, PERMANENT AVOID… or REMOVE AVOID (also on right-click). REMOVE ALL TEMPORARY AVOIDS… clears them in one go.
  - Untick "Include channels and talkgroups" for a quick read of systems, sites and departments only; STOP ends a long read.
  - You are asked before a permanent avoid and before changing more than 10 items at once. SDS-Manager 0.1.21 or later keeps permanent avoids at the next Export to Scanner.
- New tests (3).

## v1.1.76: SDS-Manager link in both editions

- **Edit in Manager…** and **Add to Favorites List in Manager…** (right-click a reception or the Scanner Information panel, and in Tools) are now in the public edition too. They need SDS-Manager installed (the sds-manager package); the request goes only to SDS-Manager on this computer.
- New: the public edition's tests cover the link (they were personal-only).

## v1.1.75: Permanent avoids survive SDS-Manager's export

- A permanent avoid (or removing one) in Scanner Tools → Favorites now says that SDS-Manager 0.1.21 or later will offer to keep it in your configuration at the next Export to Scanner. Before, exporting a configuration saved earlier quietly undid avoids made on the scanner or from the Monitor.

## v1.1.74: Warns when the scanner is out of date

- **New: a yellow warning above the Scanner Information panel** when the scanner and SDS-Manager seem out of step:
  - SDS-Manager (0.1.20 or later) has saved changes that haven't been exported to the scanner yet; or
  - the scanner is playing a Favorites List that isn't in the configuration SDS-Manager has open (the scanner may have a different configuration).
- Click the warning to hide it until it changes. It updates by itself when SDS-Manager saves or exports, and when the scanner moves to another Favorites List. Nothing is sent to the scanner.
- New tests (3).

## v1.1.73: Add what you hear to a Favorites List; names refresh by themselves

- **SDS-Manager's names, number tags and scan profiles reload by themselves** when SDS-Manager saves them: the Go to Number Tag list and Scanner Tools → Quick Keys update without pressing ↻ or RELOAD NAMES.
- Version notes in the program's comments show the version each feature came in again (a version-number update had changed them all).

## v1.1.72: Favorites List in the Scanner Information panel

- **New fields for the panel:** Favorites List (the list the scanner is playing from, or Full Database), Favorites List quick key and Favorites List number tag, read from the scanner's status messages (MonitorList, Remote Command Specification v2.00). Add them with View → Customize Scanner Information… → Add Line, use them in custom text as `{Favorites List}`, or in conditional colours (for example "Favorites List is Greenville County → blue").

## v1.1.71: Customize the Scanner Information panel

- **New: View → Customize Scanner Information…** (also on the panel's right-click menu). Choose which lines the panel shows and in what order, rename their labels or hide them, and give each line its own text colour, background, size (50–300 %) and bold. The whole panel can have its own background.
- **More to choose from.** Besides System, Site, Department, Channel, Frequency, Talkgroup, Unit ID, Mode and RSSI, there are:
  - Service type, modulation and system type;
  - the system, department and channel quick keys and number tags;
  - P25 status (NAC, colour code, RAN), hold, avoid, attenuator, scanner recording, volume, squelch and signal bars;
  - reception start time, reception length and a clock;
  - **Custom text** lines that combine fields, for example `{System} › {Department}`.
- **Conditional colours:** rules such as "Service type contains Fire → that line white on red" or "Recording is On → whole panel amber". Conditions: contains, is, is not, starts with, is empty, is not empty, number ≥, number ≤. Rules are checked in order, and later ones win.
- **Presets:** save layouts by name (for example Large print, Night), load them, or go back to the default layout. **Apply** previews the layout on the panel; **Cancel** puts it back as it was.
- Saved in `~/SDS100Monitor/info_panel.json`. Without it, the panel looks exactly as before.
- Built on 1.1.69 (1.1.70 was set aside). 8 new tests.

## v1.1.69: Readable quick key names

- **Fixed:** in Scanner Tools → Quick Keys, the "In favorites list quick key" and "In system quick key" dropdowns were too narrow to read. They are now wide enough for the names and show the key as two digits ("00 — Greenville County").
- **Fixed:** long names on the quick key buttons ran off both edges ("Spartanburg County" showed as ")1 Spartanburg Count"). The buttons are wider, four to a row, and a name that still doesn't fit ends in "…". The full name is in the button's tooltip.

## v1.1.68: Quick keys with names, number tags to pick, scan profiles

- **Quick keys show names.** Scanner Tools → Quick Keys labels each key with what it switches, for example "00 Greenville County". List names come from the scanner; system and department names come from SDS-Manager. **Only keys in use** (on by default) hides the empty ones. Green = On (scanned), grey = Off.
- **Scan profiles on the scanner.** Choose a profile saved in SDS-Manager (Favorites → Keys & Tags) and press **APPLY PROFILE TO SCANNER**. The Monitor reads each set of quick keys, then changes only the keys that differ, and reads back. Systems and departments are reached through their list and system quick keys, so items without a quick key are left alone. A list's Monitor setting can't be switched remotely.
- **Go to Number Tag** has a list of everything that has number tags in SDS-Manager's configuration ("1/2/120 — PD Dispatch (Lakeside)"). Choosing one fills in the three numbers.
- These come from a file SDS-Manager 0.1.12 or later writes when its configuration is saved; the Monitor only reads it. **RELOAD NAMES** and ↻ read it again. The names match the scanner once that configuration has been exported.
- 6 new tests.

## v1.1.67: Number tags aren't quick keys

- **Go to Number Tag explains the difference.** A number tag is a number you give a favorites list, system or channel to jump straight to it; a quick key turns scanning on and off. They are separate settings: favorites list quick key 1 is not number tag 1, and lists have no number tags until you set them. The panel says so, and when the scanner refuses a number tag (ERR) the message says what to check.
- **New QUICK KEYS… button** in the panel opens Scanner Tools on the Quick Keys tab.
- 2 new tests.

## v1.1.66: Internal changes

- No visible change in this edition.


## v1.1.65: Custom Search banks 0–9, with On / Off

- **Fixed (1.1.64):** Custom Search numbered the banks 1–10, so **TURN BANK ON / OFF** pressed the wrong number key. Banks are now 0–9, as on the scanner, and each bank's key is its own number.
- **New State column** shows each bank **On** or **Off**, from the scanner's status report while it is searching (it doesn't report banks in other modes; until then the state shows as ?). The bank being searched is marked ▶. The unclear Off column is gone.
- 2 new tests.

## v1.1.64: Custom Search; a tidier Tools menu

- **New: Tools → Custom Search…** for the scanner's own search:
  - **Search banks** read from the scanner (name, range, modulation, step). **EDIT RANGE ON SCANNER…** opens the selected bank's range in Scanner Menu; **TURN BANK ON / OFF** presses its number key while searching.
  - **START CUSTOM SEARCH** and **RESUME SCAN**, and **Quick Search Hold** from a frequency you type.
  - **Hits:** every frequency the search stops on, with how often it was heard, air time, strongest signal, talkgroup and units. Double-click to listen there; right-click to avoid it (temporarily or permanently) or stop avoiding it. **EXPORT CSV…** saves the list. Hits are also kept in reception history, as before.
- **Tools menu reorganized:** Analyze, Custom Search and Antenna Test at the top; **Scanner ▸** (Scanner Screen, Scanner Menu, Scanner Tools, Command Console), **Alerts ▸** (Activity Watch, Phone Alerts, Send Calls to Rdio Scanner) and **Maps ▸** (GPS, Places and Map, Aircraft); then Ten Codes and **Macro Keypad ▸**. The other menus are unchanged.
- 8 new tests.

## v1.1.63: Calls to Rdio Scanner

- **New: Tools → Send Calls to Rdio Scanner…** sends every recorded call (PC audio capture) to an [Rdio Scanner](https://github.com/chuot/rdio-scanner) server (free, GPL v3). Rdio Scanner plays them on your phone or in any browser, with the system, talkgroup, channel and units, and lets you replay calls and choose talkgroups. With a VPN such as Tailscale it works away from home too, on a home connection with a changing address.
  - Talkgroups are sent with their TGID; conventional channels with their frequency in kHz (155.340 MHz → 155340). Each scanner system gets a number of its own, shown and editable in the window.
  - Calls that can't be sent (server off, no network) are kept, including over a restart, and sent when it's back, oldest first (up to 500). If the server refuses the API key, sending pauses until the settings are changed.
  - **TEST CONNECTION** checks that the server answers.
- 11 new tests (the form sent, talkgroup and system numbers, retries and a real upload to a local test server).

## v1.1.62: Keypad internals

- The Macro Keypad tells other windows when an action changes. No visible change in this edition.


## v1.1.61: EXIT MENU closes the Scanner Menu window

- **✕ EXIT MENU** in Tools → Scanner Menu now also closes the window, once the scanner confirms it has left the menu and gone back to scanning. ◀ BACK still keeps the window open.
- Tests: 128.

## v1.1.60: Scanner Menu shows each change

- **Fixed (1.1.59): switching a list On or Off in Select Lists to Monitor didn't show.** The scanner made the change, but the window kept showing the old On/Off values, so it looked as if nothing happened (and a second click switched the list back). The list is now redrawn with every reply from the scanner, keeping your place in it.
- After you leave Select Lists to Monitor, the SDS100 can take several seconds (about 9 in one test) to load the lists you chose; give it a moment before pressing BACK or EXIT again.
- Tests: 126.

## v1.1.59: Every Favorites List in the Scanner Menu

- **Fixed: Tools → Scanner Menu showed only part of a long menu.** The SDS100 sends a long menu, such as **Select Lists to Monitor** with many Favorites Lists, in parts (the first 18 entries, then the rest). Only the last part was shown, so lists from Full Database to NC-Polk County were missing. The parts are now joined, and all lists are shown in the scanner's order. The Command Console still shows each part as it arrives.
- Tests: 125 (a real two-part Select Lists to Monitor reply from an SDS100).

## v1.1.58: Aircraft from ADS-B (readsb)

- **New: Tools → Aircraft (ADS-B)…** reads the aircraft list that readsb (or dump1090) writes on this computer, `/run/readsb/aircraft.json`, found automatically; or tar1090's copy, `http://127.0.0.1/tar1090/data/aircraft.json`, or any address you enter. It also reads readsb's receiver position, so distances are from your antenna. It switches itself on when readsb is found.
- **Emergency squawk alerts:** a desktop and phone alert when an aircraft squawks **7700** (emergency), **7600** (radio failure) or **7500** (hijack), or reports an emergency, with its callsign, registration, type, altitude, speed and distance. Optionally only within a distance. At most one alert per aircraft and code every 30 minutes. Phone Alerts has a new category, **Aircraft**.
- **Watch list:** callsigns, registrations or hex codes (with * for a start, such as `N911*` or `RCH*`); an alert when one is seen, at most every two hours.
- **Callsigns in airband transcripts:** *Delta twelve thirty-four*, *Southwest 2 2 1 1*, *November one two three alpha bravo* or *Cessna four five alpha* are matched to the aircraft in range at the time of the call, shown under the transcript (callsign, registration, type, altitude, speed, distance) and listed under **Heard on the radio today**. About 70 airline and operator radio names are known; a callsign not seen by ADS-B is still shown. Only airband channels (108–137 and 225–400 MHz) by default.
- Saved in `~/SDS100Monitor/adsb/` (alerts and matched callsigns, one file per day).
- Tests: 118 (aircraft.json from readsb, alerts and their limits, watch lists, spoken callsigns and numbers, matching, airband detection, the window and transcripts).

## v1.1.57: Project links

- The project page, About box and update check now point to the project's repository, https://github.com/jmlynchjr/SDS-MONITOR (1.1.56 used a repository name that doesn't exist).
- The repository's first upload (the 1.0 RC Beta zip) is replaced by the source itself; it stays in the history.

## v1.1.56: Published on GitHub

- **SDS100 Monitor is now free software under the GNU GPL v3 or later**, published at https://github.com/jmlynchjr/SDS-MONITOR with its releases (.deb downloads).
- **Help → About SDS100 Monitor** and **Help → Project Page**.
- **Check for Updates** checks the project's GitHub releases by default (you can change or clear the repository in its window).
- The README is now a general introduction; the version history moved here, to CHANGELOG.md.
- The tests run on GitHub for every change (Python 3.10 and 3.12).

## v1.1.55: Startup crash in Qt's PipeWire audio

- **Fixed: the Monitor could crash as it started** (segmentation fault; the system crash report shows it inside PipeWire while Qt Multimedia lists the audio devices). Qt 6.10 added a PipeWire audio backend, and with Qt 6.10.2 and PipeWire 1.6.2 it can crash while reading a device's audio format (the same fault prints `spaVisitChoice: parse error` at every start). The Monitor now asks Qt for its PulseAudio backend, which PipeWire serves through its PulseAudio layer, so audio capture works as before.
- To try Qt's PipeWire backend again later (after a Qt update), start the Monitor with `QT_AUDIO_BACKEND=pipewire sds100-monitor`.
- New test: the backend is chosen before Qt is loaded, and a choice you make yourself is kept.

## v1.1.54: Menu icons and quieter installs

- **Fixed: no icon in the application menu after installing the 1.1.53 package.** The menu entry named the icon by theme name, which KDE only finds once its icon caches are rebuilt. It now gives the icon's full path, and the package refreshes the icon and menu caches when it is installed or removed.
- **Check for Updates no longer causes apt's "Download is performed unsandboxed as root" notice.** apt reads packages as a restricted user that can't enter your home folder; the update is now copied to a temporary folder it can read before installing.
- Try the updater with this version: put this .deb in Downloads and use Help → Check for Updates….

## v1.1.53: .deb package and updates

- **New: installs as a Debian package** (`sds100-monitor` / `sds100-monitor-personal`), see *Install on Kubuntu*. apt handles the dependencies, the menu entry and icon are system-wide, and the two editions replace each other.
- **New: Help → Check for Updates…** (see *Updates*): newer .debs in Downloads, and GitHub releases once the project is there. One click installs (with your password) and restarts.
- The cleanup script knows about the package: with it installed, all folder installs count as old.
- Tests: 98 (versions, .deb names, Downloads, GitHub releases, skipping, installing, cleanup with the package). The build also installs each .deb into a scratch folder, makes it read-only and runs the tests from there.

## v1.1.52: Build checks

- Personal-only features are now kept out of the release candidate by the build automatically, and the build checks that none is left.

## v1.1.51: Reports open in your Firefox

- **Fixed: Daily Report → OPEN IN BROWSER said it couldn't find /snap/firefox.** It used KDE's default for .html files, which on your PC still points at a snap Firefox that isn't installed. It now uses the same browser finder as the map: `$BROWSER` if set, then the apt Firefox (`/usr/lib/firefox/firefox`), then other non-snap browsers, and KDE's default only as a last resort.
- The OpenStreetMap links inside the report window, and the links in Phone Alerts settings, now open the same way.
- New tests (81): snap browsers are skipped, the apt Firefox is used, `$BROWSER` wins, and no web link in the program goes to KDE's default handler.

## v1.1.50: Daily reports and incident summaries

- **New: History → Daily Report…** One day on one page: receptions, time on air, activity by hour, busiest talkgroups, every incident with its headline, ten codes heard, most active radios, radios not heard in the previous 30 days, places mentioned (linked to OpenStreetMap) and Weather/Tone-Out alerts.
  - **SAVE PDF…** and **SAVE HTML…** save the report you are looking at; **OPEN IN BROWSER** opens it in Firefox.
  - **Save each finished day's report automatically as PDF / HTML** (tick either or both): after midnight, each finished day's report is saved to `~/SDS100Monitor/reports` (`daily_report_YYYY-MM-DD.pdf/.html`). Days missed while the Monitor was closed are caught up, up to the last 7.
  - The PDF is made by Qt itself; no extra packages are needed.
- **Incidents: headlines.** Each incident gets a one-line summary, e.g. *10-50B Motor vehicle accident — B. Personal injury — Wade Hampton at Pleasantburg — Engine 12, Medic 4 — 7 min*: what happened (the first ten code that isn't routine like 10-8 or 10-23, otherwise the start of what was said), where (the first place mentioned), who (up to 3 units) and how long. The headline is a new column, heads the incident's details and is searchable.
- **Incidents: timeline with ten codes.** The timeline has a **Ten codes** column with the codes decoded in each call (also in EXPORT INCIDENT…).
- **Incidents: places on the map.** The places mentioned in an incident's calls are listed under the timeline; **SHOW PLACES ON MAP** opens the map on them, even for an older day outside the map's time range.
- **Fixed (since v1.1.46): call signs like "Engine niner" were no longer recognised** in Unit Name Suggestions. The ten-code feature defined its own table of number words with the same name as the call-sign table and replaced it. Found while building this version; a new test now fails if any name is defined twice.
- Tests: 76 (incident summaries and the daily report from a made-up day of history files, automatic saving, call signs, duplicate names; on your PC the real-Qt test also writes a PDF report).

## v1.1.49: No more crash on close

- **Fixed: segmentation fault every time the Monitor closed** (also with audio capture off). Your faulthandler trace showed it happened after the window had closed and saved everything, while Python shut down and PyQt6 destroyed the leftover Qt objects (`sip` during `Py_Exit`, a known problem with PyQt6 on Python 3.14). The Monitor now saves settings and then exits directly, skipping that teardown. Nothing is lost: receptions, recordings, settings and the transcription engine are all finished in the window's close step first.
- **New real-Qt test:** starts the program itself, closes it after 3 seconds and fails on a crash, an error, a process left running, or settings not saved.

## v1.1.48: Fixes from the first real-Qt test run

- **Fixed: crash (segmentation fault) when closing the Monitor** while transcription was on. The last call, saved as the window closed, was queued for transcription and started a new transcription engine after the engine had been stopped; Qt then crashed destroying a process that was still running ("QProcess: Destroyed while process … is still running"). Nothing can start the engine once closing has begun, and it is stopped again at the very end. Stopping an engine installation now also waits for it to end.
- **Fixed: Analyze window error at startup** (`'AnalyzeWindow' object has no attribute 'description'`). Qt announces the first tab while it is being added, before the description line below the tabs existed. Found by the real-Qt test on your PC.
- **Tests:** the Qt stand-in now behaves more like Qt: drop-downs, tabs, tick boxes, text and number fields send the signals Qt sends (including when the first tab or item is added), and the program's own windows raise an error for a missing attribute instead of quietly accepting it. With that, the Analyze mistake is caught here too, not only on a PC with Qt. New tests for the transcription engine on close (65 tests).

## v1.1.47: Automated tests

- **New: automated test suite** (`bash run_tests.sh`, see *Testing* above): 60+ tests covering the main window and every window and dialog, push updates against a simulated scanner, battery reading, reception logging, transcripts, Weather and Tone-Out alerts, GPS, alerts and search rules, themes, ten codes, the install and cleanup scripts, and the version number. On your PC it also runs the real program on the real Qt (see above).
- **Fixed (found by the new tests): the Weather and Tone-Out window could crash when opened** (since v1.1.42). Its alert method was called `event`, which is the name of the method Qt calls for everything that happens to a window (showing, drawing, resizing), so Qt's calls went to the alert code instead.
- **Fixed: the main window also had an attribute called `event`** (the transmission being received), which hid the same Qt method. Renamed; nothing changes in use.
- **Fixed: `cleanup_old_installs.sh --delete` listed older `-personal` installs but then skipped them.** Its final safety check before deleting didn't know the `-personal` name. They are now removed like any other older version (data folders are still never touched).
- The two editions are now made from one source, so the personal build and the release candidate can't drift apart.

## v1.1.46: Ten Codes

- **Tools → Ten Codes…** looks up ten codes and signals. Codes differ by agency, so each list says where it applies:
  - **Agencies:** words matched against the system, department or channel being received (e.g. *Greenville*). A list whose agency you are hearing is used first.
  - **Area:** a centre and range, like the scanner's location control. Lists covering where you are come next, smallest area first; lists with no area apply anywhere.
  - Your location comes from the GPS, then the scanner's own location setting, then **MY LOCATION…** in the window.
- **Show:** *Best match here* (each code once, from the best list), *All lists that apply here* (compare meanings side by side; the best is bold), or one list. Search by code (`10-50` or just `50`) or by words. **Follow what's heard** switches lists when the scanner moves to another agency.
- **EDIT LISTS…:** add your own lists, set their agencies and area (**USE CURRENT LOCATION**), turn lists on or off, and import or export CSV (`Code, Meaning, Details`). Sub-codes go in Details separated by semicolons, e.g. `B. Personal injury; C. Hit and run`. Lists are kept in `~/SDS100Monitor/ten_codes.json`.
- **Transcription window:** ten codes heard in a call are decoded under the transcript, using the list for that call's department and your location (*10-50 B* → *Motor vehicle accident — B. Personal injury*). It recognises `10-50`, `10 50`, `ten fifty`, `10-50B`, `10-50 bravo` and `signal 4`; a bare `1050` is left alone because it's usually an address. Untick **Decode ten codes** to turn it off.
- Built-in list: the APCO standard (1974) ten signals.
- Ten codes change and some agencies have dropped them for plain language; check against what you hear.

## v1.1.45: New icon

- **New program icon:** a handheld scanner with a green waveform badge. It matches the SDS100 Database & Favorites Manager's icon, which has an orange database badge, so the two are easy to tell apart in the taskbar. It shows in the window title bar, the taskbar and KDE's application menu (after running `install.sh`).

## v1.1.44: Push updates fixed

- **Push updates now work.** Your Command Console test showed the SDS100 accepts `PSI,<milliseconds>` (`PSI,1000` sent a report every second, `PSI,500` two a second, and `PSI,0` stopped it). The program sent the command correctly. But its check for "are reports still arriving?" never noticed them, because it compared Qt signal objects by identity, and Qt hands out a new object every time. So after 2.5 seconds it assumed the pushes had stopped, fell back to polling, and the tooltip said *stopped arriving*. It now checks the kind of data instead.
- Tick **Push updates** again. The status bar should read **⇣ push 250 ms**.
- If you type `PSI` commands in the Command Console yourself, the program can't tell, so set Polling to match or untick Push updates first.

## v1.1.43: RF Power Plot removed

- **RF Power Plot is gone from Tools → Analyze.** Tested on the SDS100: the scanner doesn't have it (Uniden's specification marks it as removed on the SDS100). Everything else from v1.1.42 is unchanged.

## v1.1.42: Weather Alert, Tone-Out, scanner recordings, RF Power Plot, Close Call hits, push updates

Six features from Uniden's Remote Command Specification V2.00 that the program didn't use yet. There's a new **Modes** menu.

**Weather Alert (Modes → Weather and Tone-Out…, or Modes → Weather)**
- **WEATHER SCAN** listens to NOAA Weather Radio. The alert modes keep the scanner silent until the National Weather Service sends an alert:
  - **ALERT ONLY:** any alert tone or SAME alert.
  - **SAME 1–5:** alerts for the counties in that SAME group, set up on the scanner.
  - **ALL FIPS:** a SAME alert for any county.
- When an alert comes in (the scanner opens audio, or shows an alert pop-up), the Monitor shows a **desktop notification**, sends a **phone alert**, and logs it with the scanner's alert text. Repeats of the same alert are held back for 10 minutes.
- NOAA tests the alert tone every Wednesday, usually 11 am to noon local time. That's a good time to check it works.

**Tone-Out (fire and EMS paging)**
- **LOAD CHANNELS** reads your Tone-Out channels from the scanner: name, frequency, and tones A and B.
- **▶ START TONE-OUT** monitors all of them. **HOLD ON SELECTED** monitors only one. **CHANNEL SETTINGS ON SCANNER…** opens that channel's menu.
- When the scanner hears a set of tones, you get a desktop notification and a **phone alert** (*Tone-Out: Station 5 • 154.4300 MHz • Tones 1135.5 / 832.5*), and it's logged. At most one alert per channel per minute.
- Alerts are logged in `~/SDS100Monitor/mode_alerts/mode_alerts_YYYY-MM-DD.csv` and listed under **ALERTS HEARD**.
- Phone Alerts has two new categories, **Tone-Out** and **Weather alerts**. They're on by default, even if you saved your phone settings before; untick them there if you don't want them.

**Reception history now includes Tone-Out, Weather and Close Call Hits channels.** These modes use their own channel types in the status report, which earlier versions didn't recognise, so those transmissions weren't logged or recorded. They are now:
- **System:** *Tone-Out*, *Weather* or *Close Call Hits*.
- **Department:** the tones, the weather mode, or the hits list.

So PC audio capture records a tone-out page, and transcription transcribes it.

**Scanner Recordings (Modes → Scanner Recordings…)**
- Lists the recording folders on the scanner's SD card and the recordings in each, plus the scanner's internal replay recordings.
- **▶ PLAY** (or double-click) plays a recording **on the scanner**. **◀ PREVIOUS**, **NEXT ▶** and **■ STOP (RESUME SCAN)** are beside it, and the top line shows what the scanner is playing.

**RF Power Plot (Tools → Analyze… → RF Power Plot)** *(removed in v1.1.43: the SDS100 doesn't have it)*
- Signal level (0–100) on one frequency, sampled every 100, 200, 400 or 800 ms. It doesn't need a trunked site. **USE CURRENT FREQUENCY** fills in the frequency the scanner is on.
- A large live reading, a level bar, the **peak** (and when), the 10-second average, and a graph over time.
- **MARK** records the level, peak and a note, for example *pointing NE*. That's useful for **fox hunting / direction finding** with a directional antenna, or for tracking down interference.
- Saved to `~/SDS100Monitor/rf_power/rf_power_YYYY-MM-DD.csv`.
- The scanner reports a scrolling plot of 34 bars, and the Monitor works out which values are new, so the graph keeps every sample even when status reports arrive less often.
- Uniden's specification marks parts of this function as *removed in SDS100*, and it's not clear exactly which parts. If the scanner refuses it, the window says so.

**The scanner's own Close Call hits (Close Call → Close Call Hits… → ON THE SCANNER)**
- **READ FROM SCANNER** lists the hits the scanner has stored (`GLT,CCHIT`), including ones from while the PC wasn't connected. Each shows whether it's in your log and its status there.
- **HOLD** listens on a stored hit. **USE SCANNER'S NAME** names the frequency in the Monitor with the scanner's name for it. **WATCH** alerts every time it's heard.
- The specification doesn't spell out how this list is requested. If the plain request is refused, the Monitor tries again using the Close Call Hits list's location, which it learns the first time the scanner stops on a stored hit (Close Call Hits with Scan).

**Push updates (beside Polling)**
- With **Push updates** ticked, the scanner sends its status by itself at the polling interval (`PSI`) instead of being asked each time (`GSI`). That means less traffic and fewer missed short transmissions.
- The status bar shows **⇣ push 500 ms** or **⟳ poll 500 ms**.
- If pushed reports stop arriving, the Monitor asks once more (with `KAL`, keep alive), then goes back to polling and says so. If the scanner refuses `PSI`, it polls straight away. It stops the pushes when you disconnect.
- Off by default; tick it to try it.

**Testing note:** checked with simulated scanner replies built from the specification:
- Weather Alert and Tone-Out commands, alerts and logging.
- The Tone-Out, Close Call hits and recordings lists, and playback commands.
- RF Power Plot's scrolling bars.
- Push updates: pushes arriving, pushes stopping, and the scanner refusing `PSI`.

Not yet tried on the SDS100. In particular, still to be confirmed:
- what the status report shows during a real weather alert or tone-out page;
- whether the SDS100 accepts RF Power Plot and the recordings commands;
- the form of the Close Call hits request;
- the `PSI` interval units (milliseconds assumed).

The Command Console with **XML replies** ticked shows the real replies if anything looks wrong.

## v1.1.41: Battery voltage from the scanner's screen

The SDS100 (firmware 1.26.01, the newest release) answers the battery command `GCS` with ERR, and its status report has no `Battery` field. Both appear in Remote Command Specification V2.00, which also covers the SDS150 and SDS200, and look to be implemented only on other models. But the scanner's own screen shows the battery voltage (`Batt:4.21V`) on the trunked system information view, and the program can read the screen.

- The status bar first tries `GCS`. After two refusals it reads the screen (`GST`) every 30 seconds instead, or uses the Scanner Screen's own updates when that window is open. It shows **Battery 4.21 V ≈ 100%**.
- The percentage is an estimate from the voltage of a lithium-ion cell. It reads high while charging, and the scanner charges over the USB cable. Hover over it for the time of the reading.
- When the scanner's current display doesn't show `Batt:` (for example while scanning conventional channels), the last reading stays.
- The battery reads no longer show up as "SENT: GST" in the command status line.
- At about 15% (around 3.63 V) it turns red and the status bar warns once.

**Testing note:** checked with your captured `GST` reply (4.21 V), lower voltages and a screen without `Batt:`.

## v1.1.40: Themes

**View → Theme** has three groups. Changes apply straight away to every open window, and are remembered.

- **Mode:** **Dark** (the look so far), **Light**, **System (follow KDE)** and **Night (red)**.
  - **System** reads KDE's colour scheme (`~/.config/kdeglobals`) and checks it every few seconds, so switching KDE between Breeze and Breeze Dark switches the Monitor too.
  - **Night** turns everything into dim shades of red, including charts, the Scanner Screen mirror and the waterfall, to keep your night vision. Things are told apart by brightness instead of colour. Accents don't apply in Night.
- **Accent:** **Blue** (as before), **Red**, **Green**, **Amber**, **Purple**, **Teal**. This colours tabs, menu highlights, splitters, the blue buttons and the slight tint of the backgrounds. Accent buttons keep the brightness of the blue they replace, so white text stays readable.
- **Text size:** **Small**, **Normal**, **Large**, **Extra large**. This scales all text, including chart labels and the information panel.

**What stays the same in every theme**
- Status colours keep their meaning: green good, amber warning, red bad, cyan control channel. In Light they're darker shades, checked for at least 4.4:1 contrast against the darkest light panels.
- Coloured action buttons (START, STOP, AVOID…) keep their colours with white text.
- The Scanner Screen mirror keeps the scanner's own display colours (except in Night).
- The waterfall keeps its signal-strength colour scale (except in Night).

**How it works:** every colour in the program now goes through the theme. The original dark colours act as names: each has a role (background, text, status, button, accent or scanner colour), and the theme works out what that role looks like in the chosen mode and accent. New windows and features follow the theme automatically.

**Testing note:** the theme colours were checked for contrast and drawn as previews of each mode and accent. The program was built and switched through every option with stand-in Qt classes. The real windows couldn't be opened here, so look over a few windows in Light and Night on your PC. If anything is unreadable, a screenshot is the quickest way to show me.

## v1.1.39: Analyze tools and fixes from testing on the scanner

Built from your console captures of Analyze on the Palmetto 800 site (system 1D9, site 2-023). Current Activity, Activity Log, LCN Monitor and System Status all work on the SDS100. **Tools → Analyze…** now has:

**Site health over time** (System Status tab)
- While System Status runs, signal (S), decode quality (Q) and activity (A) are averaged every few seconds (**Average every**, default 10 s) and drawn as a graph, with the lowest Q in each interval.
- **Low decode below** (default 50) draws a line on the graph and counts the intervals that dropped under it, with the time of the last one.
- Saved to `~/SDS100Monitor/site_health/site_health_YYYY-MM-DD.csv` (can be turned off). Leave it running for hours to see dropouts and time-of-day patterns, or to back up the Antenna Test with a longer run.

**Channel load** (Current Activity tab, below the table)
- **Busy now:** how many voice channels have a call on them right now.
- Since the start: average busy, peak (and when), transmissions per minute and how long all voice channels were busy at once.
- Graph of average and peak busy channels per minute. Saved to `~/SDS100Monitor/channel_load/channel_load_YYYY-MM-DD.csv`, one line per minute.
- Right after Current Activity starts, the scanner lists only the channels it has seen so far. The program remembers the most channels each site has shown, so a short list doesn't count as "all busy".

**Found IDs** (new tab)
- Every talkgroup and unit seen in Current Activity and the Activity Log, including ones you don't scan, with how many transmissions, when first and last seen, who they were heard with, and notes (encrypted, patched with…, the scanner showing the type as "Unknown").
- **Status** is checked against your reception history, unit ID log and unit names: **New** (never logged by the Monitor), **Heard, no name** / **Seen before**, or **Named**. Talkgroups take their name from reception history; units from your unit names.
- **Show:** New only / Not named / All, plus talkgroups or units and a filter box. Right-click for **Name This Unit…** and the other unit actions, **Alert When Talkgroup Is Active**, **Search Everything**, Copy and Remove From List.
- Kept between sessions in `~/SDS100Monitor/analyze_found_ids.csv`. **RE-CHECK** re-reads history (done automatically when you open the tab and each new day); **CLEAR LIST…** starts over.
- Talkgroups are matched by number only, whatever the system.

**Fixes**
- **Selecting a tab doesn't change what the scanner is doing.** Before, clicking the Activity Log tab while Current Activity was running just showed an empty table. Now the running function's tab has a **●**, the other tabs say what's running, and START becomes **▶ SWITCH TO …**, which stops the current function and starts the new one.
- **Current Activity colours** now show real calls. The scanner re-sends every channel 5 times a second, so before every row was always green. Now: green = call on the air, amber = call ended in the last 10 s, blue = control channel, red = encrypted, grey = idle. New columns: **Talkgroup name** (from reception history), **On air** (how long the current call has lasted) and **Last call**. Named units show their name.
- **Activity Log:** the scanner labels the P25 synchronization (time) broadcast "Add Harris Patch ID". It made up about 70% of your log, every 0.4 s. These are now hidden and not saved; **Show sync broadcasts** brings them back. Lines the scanner sends twice are dropped, and the quotes around the data field are gone.
- **LCN Finder** on a P25 site now explains that it only works on EDACS, LTR, MotoTRBO and DMR Tier III, instead of a generic refusal.
- **Battery:** your SDS100 answers the battery command (GCS) with ERR, even on USB power. After two refusals the Monitor stops asking (no more ERR every 30 seconds) and shows "Battery: not reported". It tries again on the next connection.

**Noticed in your captures:** the scanner's clock was about 22 seconds slow compared with the PC. **Set Clock from PC** fixes that, which helps when lining the Activity Log up with recordings.

**Testing note:** the channel load, Found IDs and Activity Log changes were tested by replaying your two console captures through the new code. Site health was tested with simulated values, because the captures had no status reports. The windows themselves couldn't be opened here, so look over the new layouts on your PC.

## v1.1.38: fixes for v1.1.37

- **v1.1.37 wouldn't start** (`'Monitor' object has no attribute 'close_call'`): the Close Call menu was built before the parts it uses. They are now created first.
- **"Could not parse stylesheet of object QPushButton" messages** in the terminal are gone. Eight button styles (Discovery, Scanner Screen, Analyze, Scanner Menu, Antenna Test, Close Call, the control buttons and the waterfall panel) had a stray `}` and Qt ignored them, so those buttons now show their intended colours and rounded corners. This dates back several versions; nothing else changed.

## v1.1.37: Close Call menu

A **Close Call** menu next to Discovery:
- **Close Call Hits…** opens the Close Call window (below).
- **Mode: Off / Priority / Do Not Disturb** sets the scanner's Close Call mode. The tick shows the mode last set or read from here. **Check Current Mode** reads it from the scanner.
- **Start Close Call Only** and **Resume Scan**.
- **Close Call Bands…** and **Close Call Settings on Scanner…** open Tools → Scanner Menu straight onto those menus.

**How the mode is set:** the remote commands have no Close Call mode command, so the program opens the scanner's Close Call menu (`MNU,CC`), reads it (`MSI`) and picks the items by what they're called, never by position: first the item with "Mode" in its name, then *Off*, *Priority* or *Do Not Disturb*, and then it leaves the menu. If the menu doesn't look like that, it stops where it is and opens the Scanner Menu window there, so you can finish by hand. Your scanner's real menu wording will show whether it works on the first try.

**Close Call Only** uses `JPM,CC_MODE` and checks the status report for *Close Call Only*. If the scanner refuses JPM, it chooses *Close Call Only* from the Close Call menu instead.

**Close Call window:**
- **Scanner:** mode buttons, CHECK, CLOSE CALL ONLY, RESUME SCAN, BANDS…, CC MENU…, and what the scanner reports right now.
- **Frequencies heard:** one row per frequency, showing name, status, hits, days heard, first and last heard, best RSSI, time on air, tone/ID and notes. It covers Today, the last 7 or 30 days, or everything. It's built from reception history, so every Close Call hit logged since v1.1.14 is already there.
- **Status per frequency:** *New*, *Known* (no new-frequency alert), *Watch* (alert every time it's heard, at most every 5 minutes) or *Ignored* (no alerts, hidden unless *Show ignored* is ticked). Double-click a frequency or press NAME / NOTES… to name it ("Fireground 1"). Names and notes are saved in `~/SDS100Monitor/close_call_frequencies.json`.
- **HOLD** listens on the frequency (Quick Search Hold, the same as *Tune to frequency*). **SEARCH EVERYTHING** looks the frequency up in history, transcripts and the rest.
- **Hits:** every logged hit on the selected frequency. Right-click a hit for details, its PC recording, or to export the hits.
- **EXPORT CSV…** saves the frequency list.

**Alerts:**
- *New Close Call frequency*: a frequency Close Call has never logged before. It's optional, and you can set a minimum signal so weak, distant hits don't alert. These alerts start after 3 days with Close Call hits, so the first day doesn't alert on everything.
- Alerts use the usual Alerts settings (desktop notification, sound). For your phone, they're a new category in Phone Alerts: *New Close Call frequency / watched frequency*. If you've saved phone settings before, tick that category there; it's off until you do.
- Activity Watch no longer gives a *New talkgroup heard* alert for Close Call hits, so you don't get two alerts for the same frequency.

**Untested on the scanner:**
- The Close Call menu's real item names. The program reads them, and anything unexpected ends in the Scanner Menu window rather than a wrong choice.
- `JPM,CC_MODE` (the spec reserves its index field; `0` is sent, then a blank one).
- What the status report calls the mode during a **Close Call Priority** hit while scanning. Hits are recognised by "Close Call" in the scanner's mode (e.g. *Close Call Only*). If Priority hits don't show up in the window, a Command Console capture of `GSI` during one will show what it uses.

This was checked against simulated menu replies (expected layout, unexpected layout, refused commands, the RSV retry, timeouts) and generated history, not the real SDS100.

## v1.1.36: Antenna Test (Tools → Antenna Test…)

Compares antennas, mounts or positions on the same real signals. The scanner's readings aren't calibrated, so this is an A/B tool: the same scanner, coax and place, with only the antenna changed, run close together in time. It can't measure SWR, impedance or true gain. A NanoVNA does that, and pairs well with this.

**References tab:** the signals to measure, in order. Each has a type that sets how it is sampled:
- **P25 site (control channel):** for the Palmetto 800 Greenville simulcast. Scan or hold on the site, then **ADD CURRENT SITE**. The test runs the scanner's own *Analyze → System Status* and records **Decode Quality (Q)** and **Signal (S)**. For a simulcast, **Q is the number that matters**: an antenna that hears more of the out-of-phase towers can show more signal and decode worse. Optional **voice window:** afterwards it holds the site (HLD,SITE) and counts calls and how many were decoded. Traffic varies, so treat the call count as supporting evidence.
- **Continuous signal:** NOAA (**ADD NOAA…**, or hold on it and **ADD CURRENT FREQUENCY**). Every reading during the hold is used. It also reports the spread between strong and weak readings (fading/multipath).
- **Bursty / repeater:** for VHF DMR. Readings are only used while a signal is present (squelch open or at least one signal bar), and transmissions are counted. Defaults to 20 minutes; give it 15–30.
- **Noise floor:** an empty frequency in a band. Lower is better. Also shows how often something broke squelch there (interference).

Frequencies are tuned with Quick Search Hold, the same as *Tune to frequency*. The run skips anything the scanner doesn't confirm within 15 seconds and says so.

**Run tab:** give the run a label (*Antenna A*, *Roof mount 20 ft*), add notes, and press **START RUN**. Live readings, progress and per-reference results are shown as it goes. **SKIP** keeps what a reference has so far; **STOP** keeps everything measured. The scanner goes back to scanning at the end (optional). Every run is saved to `~/SDS100Monitor/antenna_tests` as it happens, including a stopped one or one cut off by a disconnect.

**Waterfall noise-floor snapshot (Run tab):** with the scanner in waterfall mode on a band, **CAPTURE SNAPSHOT** averages 20 frames and adds them to a session. Use the same center, span and RF gain for every antenna. Levels are the scanner's raw waterfall units, not dBm.

**Compare tab:** tick sessions to compare. Each reference gets a row per measure, with the difference from the oldest ticked session and a **Best** column. A difference only counts when it is bigger than about 2 dB (RSSI), 5 points (Q/S) or 20% (counts); otherwise it says *≈ no clear difference*. There's also a grouped bar chart per measure, and overlaid waterfall traces for snapshots of the same center and span.

**Drift check:** finish by running the first antenna again **with the same label**. The Compare tab measures how far those two runs differ, which is how much conditions moved on their own, and won't count any difference smaller than that.

**Export:** **EXPORT SUMMARY…** (one CSV row per session and reference, all measures) and **EXPORT READINGS…** (every reading).

**Untested on the scanner:**
- That GSI reports RSSI with the squelch closed (noise floor) and while Analyze is running. If it doesn't, the result says so and signal bars are still recorded.
- That `HLD,SITE` holds a site. If the scanner refuses it, calls on that site are counted while scanning instead, with a note.
- That Quick Search Hold decodes DMR. If *Decoded while signal present* is 0% while signal is present, RSSI and the transmission counts are still valid.

This was checked against a simulated scanner (three sessions, refused commands, a stop, a disconnect, snapshots), not the real SDS100.

## v1.1.35: Lower memory use

Nothing looks or works differently, apart from a short pause on the first call transcribed after an idle spell.

**Transcription engine** (measured at about 1.3 GB with the Small model):
- **Unloads when idle:** the model unloads after **5 minutes without calls** (Transcription → SETTINGS… → *Unload the model after*; *Never* keeps it loaded). The engine process then uses no memory at all. The next call loads it again, which takes a few seconds; a call that arrives while it's unloading isn't lost.
- **Hands memory back:** while loaded, it returns memory to the system after each call and uses fewer memory pools (`MALLOC_ARENA_MAX=2`), which usually keeps it noticeably smaller.
- **Shows its size:** the status line shows how much memory the engine is using (e.g. *Ready: small.en on CPU • using 1.1 GB*). The settings list rough sizes per model: Base uses about half of Small.

**The Monitor itself:** windows that read your whole history no longer keep it all in memory. Checked against 4 months of generated traffic (204,000 receptions), with identical results before and after:
- **Activity Charts:** keeps totals per day, hour and channel instead of every reception: 51 MB → 5 MB.
- **Unit Profile:** reads the unit ID log one day at a time and keeps only what the profile shows, for each profile opened: up to 169 MB → 30 MB.
- **Unit ID Log:** reads only the chosen period (Last 30 days by default) instead of all history, so changing the period now reloads it: 124 MB → 32 MB.
- **Activity Watch:** keeps two running totals per talkgroup and hour instead of a counter for every 15-minute slot; alert decisions are unchanged.
- **Closing windows frees their data:** Search Everything, Fleet Map and Incidents let go of their results when closed and reload when reopened (Search reruns the last search).
- **Memory goes back to the system:** after these big reads, and after loading history at startup, freed memory is returned to the system instead of staying reserved by Python.

**Testing note:** results were compared between v1.1.34 and v1.1.35 on the same generated history, and the engine's idle unload was checked with the real worker process and a stand-in speech engine. The real faster-whisper engine's memory with these settings hasn't been measured. The status line will show it.

## v1.1.34: GPS and places on a map

### GPS keeps the scanner's location updated (Tools → GPS…)

The SDS100 takes a GPS receiver on its mini-USB port, which the Monitor uses for the PC connection, so the two can't share it. Instead, the Monitor reads a GPS on the PC and sets the scanner's location with the remote **LCR** command as you move, so location-based scanning keeps working while the scanner is connected (for example, a laptop in a vehicle).

- **USB GPS receiver:** most pucks (u-blox, BU-353…) show up as `/dev/ttyACM0` or `/dev/ttyUSB0`. The scanner's own port is left out of the list. Speed is detected automatically (4800 to 115200 baud). If the port won't open, run `sudo usermod -aG dialout $USER`, then log out and back in.
- **Android phone:** install **GPSd Forwarder** (free, on F-Droid), enter the PC's address (shown in the dialog) and the UDP port (default 29998), and tap Start. Phone and PC must be on the same Wi-Fi. Any app that sends NMEA over UDP works.
- **iPhone or another device over TCP:** an NMEA app that runs a TCP server (for example *NMEA GPS*) shows the address and port to enter. iOS stops such apps after a while in the background, so keep it open.
- **gpsd**, if you already run it (default 127.0.0.1:2947).
- **How it updates:** the Monitor first reads the scanner's location to learn its number format and range, then sends your position once you've moved **0.5 miles** (adjustable), and at least every **10 minutes** while moving, but never more than every 30 s. The scanner's own range is kept unless you set one. Updates restart after a reconnect.
- **⌖ GPS** in the status bar: green with a fix, amber while waiting for one or after losing it, red on an error. Hover for position, speed and satellites, and when the scanner was last updated; click for the settings.

### Places from transcripts (Tools → Places and Map…)

- **What's picked out of transcripts:** addresses (*400 Main Street*, *1234 N. Elm Ave*, *200 block of Smith Lane*), intersections (*Main and 5th*, *Route 40 at Oak Ridge Road*, *corner of Potomac Street and Franklin Street*), and your **landmarks**. Call signs such as *Engine 12 and Medic 4* aren't mistaken for intersections.
- **Lookups:** addresses are looked up with OpenStreetMap's Nominatim, intersections with OpenStreetMap's Overpass (where the two streets actually meet). If no meeting point is found, the place is put on the first street and marked **approximate** (dashed on the map).
- **Area:** set your **Area** (e.g. *Hagerstown, MD*) and radius. With GPS on, places near you are preferred; otherwise near the scanner's own location.
- **Respecting the services:** lookups are cached (`~/SDS100Monitor/geocode_cache.json`) and kept to one a second, as the services ask. The map tiles come from openstreetmap.org (© OpenStreetMap contributors).
- **Landmarks:** one per line as `Name = latitude, longitude` (e.g. `North High School = 39.6512, -77.7134`). Saved places from Scanner Tools → Location count automatically. Right-click a place → **Add as Landmark…** to reuse a corrected position.
- **The window:** the places for each day (time, place heard, found as, status, channel, units, transcript). Double-click shows a place on the map. Right-click: Play Call, Open in OpenStreetMap, Copy Position, **Correct Position…**, **Not a Place** (hides it). **FIND PLACES IN THIS DAY'S TRANSCRIPTS** does older days. New transcripts are checked automatically (switchable).
- **The map** opens in your browser (Firefox from apt is preferred over a snap browser). It's served by the Monitor on this computer only, protected by a random key in the address. Markers are coloured by age (red under 1 h, orange under 6 h, yellow under 24 h, blue older). Click one for the time, channel, units and transcript, and ▶ Play to hear the call. A side list shows the newest first; click an entry to zoom to it. Choose 1 h to 7 days. Your GPS position and the scanner's location range are shown, with **follow GPS** to keep the map on you. The map refreshes every 10 s.
- **Files:** `~/SDS100Monitor/places/places_YYYY-MM-DD.csv` (Time, System, Department, Channel, Talkgroup, Unit IDs, Place, Kind, Latitude, Longitude, Found as, Status, Audio File, Transcript).
- **Needs:** transcription (v1.1.28) for places, and an internet connection for lookups and map tiles.

**Testing note:** NMEA parsing and the USB, UDP, TCP and gpsd sources were checked with real sockets and a simulated serial port, along with the LCR updates, address and intersection finding (including phrases that must not count), the lookups against stand-in Nominatim and Overpass servers, and the map page. Not yet run with a real GPS, phone, scanner or the real OpenStreetMap services. Untested: the scanner's actual LCR reply format, which the Monitor reads first (if it isn't plain decimal numbers, the GPS dialog says so and asks for the reply), and how often the scanner accepts location updates while scanning.

## v1.1.33: Search Everything and Fleet Map

**History → Search Everything… (Ctrl+F, from any Monitor window)** searches everything in one place: reception history (calls), transcripts, radios and incidents. Each kind gets its own tab, with its count.
- **How to search:** all words must match, in any field; use "quotes" for a phrase (`"main street" fire`). Talkgroup IDs, frequencies, channel names, unit IDs (`UID:3239937`), unit names and their notes all work.
- **Searching by a name finds the radio's ID too:** searching `engine 12` also finds transcripts and incidents that only recorded the radio's number, as long as you've named it in the Monitor.
- **Range:** Today, Last 7 / 30 / 90 days, or Everything (remembered). Incidents are worked out from each day's calls, so they're searched for the last 14 days of the range. Up to 2,000 results of each kind are shown (the tab shows "+" when there are more). Searches run in the background, and a new search replaces one still running.
- **Double-click:** a transcript plays it; a call plays its recording (or shows its details if there isn't one); a radio opens its unit profile; an incident opens Incidents at that incident. Right-click for more (copy, unit names, search for this channel).

**History → Fleet Map…** sketches which agency, unit type or shift each radio belongs to, from the unit ID log (last 7 / 30 / 90 days or everything).
- **Fleets:** a radio's fleet is the talkgroup it keys up on most. Each fleet shows how many radios it has, keyups, active hours (the hours holding 90% of its traffic, e.g. 07–15), other talkgroups it uses, when it was last heard, and the first word of its named radios (e.g. *Engine*).
- **ID blocks:** within a fleet, radios are grouped into blocks of nearby ID numbers (within 100, adjustable), since agencies often number radios in ranges. Different blocks with different active hours often mean shifts or units: for example, IDs 20100–20107 active 07–15 and 20500–20505 active 15–06.
- **Radios:** each shows its ID and name (the scanner's own name in [brackets] if you haven't named it), keyups, active hours and other talkgroups. Unnamed radios show the nearest named radios in their block (*near Engine 12, Engine 15*), a hint at what they are. Radios on 5 or more talkgroups, or named Dispatch/Console, are marked *console / command radio?*.
- **Talkgroup grid:** select a fleet, block or radio to see its radios against the talkgroups they use, shaded by keyups.
- **Actions:** double-click a radio for its profile; right-click to name it or search for it; copy a block's radio IDs. Filter box, **Unnamed radios only**, and EXPORT… to CSV.

**Better dispatch detection in Incidents:** a radio used to count as dispatch if it was heard near 6 or more other radios. On a busy day a busy engine company can do that too, which dropped it out of its own incidents. Now a radio also has to be on at least 15% of the calls on a busy talkgroup (30 or more calls a day), which a dispatcher is (roughly half of dispatch traffic) and a field unit isn't. Radios named Dispatch/Console still always count.

**Testing note:** checked against 41 days of generated traffic (three agencies, numbered radio blocks, day and night shifts, a dispatch console, transcribed calls) and all the earlier tests; not yet run on your real history or on Kubuntu's Qt. Untested: the two windows themselves and search speed on months of real history.

## v1.1.32: Phone alerts and an Activity Watch ignore list

**Activity Watch ignore list:** busy channels like dispatch no longer set off unusual-activity alerts.
- Right-click a talkgroup in Activity Watch → **Ignore …**, or use **IGNORE LIST…** and type a talkgroup ID (`TGID:44002` or `44002`), a channel name, or a word in the name: **Dispatch** ignores every channel with Dispatch in its name, including ones heard for the first time later. While typing, the list shows which recently heard channels match.
- Ignored talkgroups give no unusual-activity or new-talkgroup alerts; they stay in the table, greyed, as *ignored*. Right-click → **Alert for … Again** removes whichever entry covers it (for a word entry such as Dispatch, that's every channel it covers).
- New and returning radios heard on an ignored talkgroup still alert, since a new radio on dispatch can be interesting; tick **No radio alerts from ignored talkgroups either** to stop those too.

**Phone alerts** (Tools → Phone Alerts…, or PHONE ALERTS… in Activity Watch and in Alerts) send alerts to your phone as push notifications.
- Ordinary text messages aren't an option any more: AT&T (June 2025) and T-Mobile have shut down their email-to-text gateways, Verizon is phasing out vtext.com, and sending real SMS now needs a registered business account. Push notifications arrive on the lock screen the same way.
- **ntfy** (recommended, free, no account): install the ntfy app (Android or iPhone), tap +, and subscribe to the topic shown, which is a random name such as `sds100-3f9a1c7e2b`. Keep it random: anyone who knows a topic name can read it. Priority Normal, High (default) or Urgent (on Android, Urgent can break through Do Not Disturb). A self-hosted ntfy server with an access token works too.
- **Pushover** (application token + user key), **Telegram** (bot token from @BotFather; send your bot /start, then FIND CHAT ID fills in the chat ID), or **Email** (any SMTP server; for Gmail use smtp.gmail.com, port 587, STARTTLS and an app password).
- **Choose what goes to the phone:** unusual activity, new talkgroup and keyword alerts are on by default; new radios, returning radios and other alert rules can be added. **No more than 20 a hour** (adjustable) and optional **quiet hours** (e.g. 22:00 to 07:00). Alerts still show on the PC during quiet hours and over the limit.
- **SEND TEST MESSAGE** tries the settings before you save them and shows the service's reply if it fails. Failed alerts are reported in the status bar.
- Settings, including tokens and passwords, are stored in the Monitor's settings file in your home folder (`~/.config/SDS100Monitor/`).

**Testing note:** the requests to ntfy, Pushover and Telegram, and email delivery, were checked against local stand-in servers, along with the ignore list, quiet hours and the hourly limit; not yet sent to a real phone or run on Kubuntu's Qt. SEND TEST MESSAGE is the quickest check.

## v1.1.31: Incidents, unit name suggestions and Activity Watch

Built on v1.1.29 (transcription stays in its own window; the v1.1.30 panel was set aside). All three features work from files the Monitor already keeps: reception history, the unit ID log and transcripts. Reception history has no unit column, so each call's radios are matched from the unit ID log by system, channel and time.

**History → Incidents…** joins calls into incidents and shows each one as a timeline.
- Two calls belong together when the same radio is in both, up to **10 min** apart (adjustable), or when they follow each other on a talkgroup within 30 s and a field unit is in one of them (dispatch, then a unit answering). An incident needs **3 calls** (adjustable).
- Dispatch consoles talk with nearly every radio, so they would join everything. A radio heard with 6 or more different radios (today plus the day before) is treated as dispatch, and so is any radio you've named with *Dispatch*, *Console*, *Comm*, *Control*, *911*, *ECC* or *Base*. The window lists which radios it treated as dispatch.
- The list shows start, length, calls, units, talkgroups, notes (*units moved to Fireground 2*, *more than one agency*) and what was said (the first transcribed call, usually the dispatch). Select an incident for its timeline: time, +minutes, talkgroup, units (with your names), length and transcript. Double-click to play a call; right-click for unit names and profiles. Search covers words said, talkgroups and units. EXPORT INCIDENT… saves it as text or CSV. Today's incidents refresh every minute.
- Calls with no unit ID (analog, or ended before the ID arrived) only join when they answer a unit within 30 s, so incidents work best on P25/DMR systems.

**History → Unit Name Suggestions…** learns radio names from transcripts.
- When a radio is the only one on a transcribed call and the speaker starts with a call sign (*Engine 12 on scene*, *Dispatch, Medic 4 en route*, *Engine one two available*), that's a vote for the radio's name. A suggestion needs **2 votes** and **60%** of the radio's call-sign calls; **High** confidence is 4 or more votes and 80% or more.
- A radio that gives several different call signs is marked *probably a dispatcher or a shared radio* and gets no suggestion.
- ACCEPT AS GUESS / ACCEPT AS CONFIRMED names the radio (notes say how many calls it came from); NOT THIS NAME stops that suggestion for good; UNIT PROFILE… opens the radio's profile. The lower list shows the calls behind a suggestion; double-click to listen.
- New suggestions appear in the status bar as calls are transcribed. **Name unnamed radios automatically** (off by default) names High-confidence radios as Guess. Names you've given are never replaced.
- CALL-SIGN WORDS… sets the words that start a call sign (Engine, Medic, Car, Adam, Deputy Chief…). A number must follow, as digits or words.

**Tools → Activity Watch…** learns each talkgroup's normal traffic and alerts when something's different.
- **Unusual activity:** each talkgroup's or channel's calls in the last **15 min** (10/15/30) are compared with its normal for that hour of the day, learned from the last **28 days** (14/28/56/90). Hours when the Monitor wasn't running don't count as quiet. Sensitivity Low/Medium/High alerts at 4×/3×/2× normal (and well above the usual variation), with at least **6 calls**. One alert per talkgroup per 30 min.
- **First heard:** a talkgroup or channel, or a radio, heard for the first time in your history; **back after a quiet spell:** a radio not heard for **30 days** (adjustable). New radios can arrive in bursts (mutual aid, a new fleet), so they give at most one notification a minute; the rest go to the log.
- The window lists everything heard in the last few minutes, most unusual first (calls now, normal for now, state: UNUSUAL / busy / normal / learning), plus a log of activity alerts.
- Alerts start once there are **7 days of history**. Notifications use the Alerts settings (desktop notification, sound) and appear in Alerts → Recent alerts. Normal levels are re-learned each day.

**Testing note:** checked against 20 days of generated traffic (dispatch consoles, field units, a structure-fire incident moving to a fireground talkgroup, transcribed calls) and all the earlier tests; not yet run on your real history or on Kubuntu's Qt. Untested: the windows themselves, and how the thresholds feel with your traffic. The settings above are the knobs to adjust.

## v1.1.29: Transcription fix

- **Fixed:** every call failed with "Couldn't transcribe … unexpected keyword argument 'metadata_errors'". The current faster-whisper release (1.2.1) passes an option to its audio library, PyAV, that PyAV 19 removed, so a fresh install broke on every file. The transcription worker now decodes recordings itself with ffmpeg (already installed for PC audio capture) and gives Whisper the audio directly, so PyAV is no longer used. **No reinstall needed:** install v1.1.29 and press TRANSCRIBE THIS DAY to redo the calls that failed.
- INSTALL ENGINE now also keeps PyAV below version 19, so new installs stay consistent.

## v1.1.28: Transcription

**View → Transcription…** shows what was said on each recorded call, newest at the top, as calls come in.

- **Works on PC AUDIO CAPTURE recordings.** Every new MP3 is transcribed automatically (switch this off with **Transcribe new calls**). **TRANSCRIBE THIS DAY** does a day's older recordings; new calls go ahead of them.
- **Runs on this computer, offline.** It uses Whisper (the faster-whisper engine). No audio leaves the PC and there's no account or cost.
- **One-time setup:** in the Transcription window, SETTINGS… → **INSTALL ENGINE**. This downloads faster-whisper (about 300 MB) into `~/SDS100Monitor/transcribe-engine`, a separate Python environment, so nothing else on the system changes. It needs `sudo apt install python3-venv`. The chosen model downloads the first time it's used (the status line shows progress). Tick **Include NVIDIA GPU support** before installing if you have an NVIDIA card (about 3 GB more). If the GPU won't run, the engine switches to the CPU by itself.
- **Models:** Small (English) is the default and a good balance on a CPU. Base or Tiny are faster on an older PC; Medium is more accurate but slow without a GPU. Large v3 and Distil large v3 are meant for an NVIDIA GPU. Change the model, language and beam size in SETTINGS…; the engine restarts with the new settings.
- **Vocabulary:** list the names and words your agencies use (unit names, stations, streets, codes like 10-4) and Whisper will expect them. The call's channel, department and system names, and your unit names from v1.1.26, are added automatically. This makes the biggest difference to accuracy.
- **The window:** time, channel, talkgroup, units (with your names), length and transcript. Search covers the words said as well as channel, talkgroup and unit. **Only calls with speech** hides recordings where nothing was understood. Double-click or ▶ PLAY to listen. Select a call to read it in large type below the list; fix mistakes there and press **SAVE CORRECTION** (the model column then says "(corrected)"). **TRANSCRIBE AGAIN** redoes one call, e.g. after changing the model or vocabulary. **EXPORT…** saves the current view as CSV, or as plain text with one line per call.
- **Keyword alerts:** Alerts has a new **Transcript** field, e.g. Transcript contains `structure fire`, which gives a notification like *Heard "structure fire" on Fire Dispatch* with what was said. Add one from KEYWORD ALERTS…, or right-click a call → Alert When Transcript Contains… (text you've selected in the transcript is filled in).
- **Files:** `~/SDS100Monitor/audio/YYYY-MM-DD/transcripts_YYYY-MM-DD.csv`, beside the day's MP3s and recordings index (Start, System, Department, Channel, Talkgroup, Unit IDs, Audio Length, Audio File, Transcript, Model, Transcribed). The MP3s and the recordings index aren't changed.
- Whisper sometimes "hears" words in noise; transcripts that are only a known phantom phrase ("Thank you.") and segments Whisper itself marks as probably not speech are dropped. Digital (P25/DMR) voice and weak signals transcribe less well than clear analog audio.

**Testing note:** the worker and the Monitor's queue, saving and keyword alerts were checked with a stand-in for the speech engine; not yet run with the real faster-whisper or on Kubuntu's Qt. Untested: installing the engine, model download progress, GPU use, and transcription accuracy on real scanner audio.

## v1.1.27: Macro keypad

Control the scanner from a cheap USB macro keypad: the "MINI KeyBoard" pads with 1–16 keys and 0–3 knobs that show up as `1189:8890` in `lsusb`. **Tools → Macro Keypad…** sets it up.

- **Works in the background.** The Monitor reads the keypad directly (`/dev/input`), so its keys work while another window is in front. With **Keypad keys go only to the Monitor** (on by default), the keypad stops typing into other programs while the Monitor is running. It goes back to normal when the Monitor closes.
- **One-time setup:** `sudo bash install_keypad_rule.sh` (in the installed folder), then unplug and replug the keypad. This lets your user read and program the keypad without sudo. Without it, the keypad works only while a Monitor window is the active window. The window's SETUP HELP button shows the same steps.
- **PROGRAM KEYPAD…** gives every key and knob action its own code, so each one can do something different: Key 1–12 → F13–F24, Key 13–16 → Ctrl+F13–F16, knob turns and presses → Shift+F13–F21. It uses the keypad's own configuration protocol (the same one as the Windows MINIKeyBoard tool), reads the number of keys and knobs from the pad, and asks before writing. This replaces what the keys did before, such as settings made with minikeyboard.
- **LEARN:** if your keypad is already programmed the way you like (for example with media keys on the knob), click LEARN on a row and press the key. Whatever the key sends is recorded. Two rows can't share the same key.
- **Actions:** scanner control (resume scan, channel/system/department hold, previous/next, temporary avoid and remove avoid, each with or without the confirmation question, weather scan); audio (volume ±, mute, squelch ±, recording on the scanner, PC audio capture on/off); any scanner key, including the knob ◀ / push / ▶; FUNC combinations (attenuator, IF Exchange, display, priority, search keys, and FUNC + hold 4/9/REPLAY); waterfall controls; and opening the waterfall, Scanner Screen or Analyze, bringing the Monitor to the front, or connecting/disconnecting.
- **Defaults:** Key 1 resume scan, 2 channel hold, 3 temporary avoid (asks first), 4 system hold, 5 department hold, 6/7 previous/next, 8 recording, 9 REPLAY, 10 FUNC, 11 MENU, 12 E/YES. Knob 1 is volume (press mutes), knob 2 is squelch, and knob 3 is the scanner's knob. Change any of them in the window; DEFAULT ACTIONS puts them back.
- Press a key on the keypad and the window highlights its row, with what it sent and what it did. The status bar shows every keypad action, unassigned keys, and presses that were ignored because the scanner isn't connected or a dialog is open.
- Settings are remembered (`keypad/…` in the Monitor's settings).

**Testing note:** checked with a simulated keypad (fake device nodes and input events) and the byte-for-byte protocol from the vendor's tool; not yet tried with the real keypad or on Kubuntu's Qt. Untested on hardware: programming the pad, grabbing it, and the fallback that catches keypad codes in the Monitor's own window when `/dev/input` can't be read.

## v1.1.26: Unit names and unit profiles

The SDS100 reports a P25 unit's number (UID) but not the name some radios send over the air (talker alias), and no GPS location. So unit names are now kept by the Monitor itself, with tools to help work out which ID is which.

- **Name This Unit…** Right-click a unit and choose Name This Unit… to give it a name, a status (**Confirmed** or **Guess**) and notes. You can do this from Scanner Information, the Unit ID Log, reception history (a submenu for each unit logged during that reception), Audio Recordings, a unit profile and Analyze → Current Activity. Names are saved in `~/SDS100Monitor/unit_names.csv`, which you can also edit in a spreadsheet.
- **Names show everywhere:** Scanner Information, the Unit ID Log, alerts, the Unit IDs in MP3 tags and the recordings index, and Discovery hits, e.g. `Engine 12 (UID:3239937)`. Guesses carry a ?, e.g. `Medic 4? (UID:3239940)`. A name given in the Monitor wins over a name programmed in the scanner. The unit ID log CSV still records the scanner's own name, so its format is unchanged.
- **Unit profile** (double-click a unit in the Unit ID Log, or History → Unit Profile… and type an ID):
  - **Recordings:** every saved recording that includes the unit, newest first. Double-click or PLAY NEWEST. Units often say who they are on the air, so this is usually the fastest way to identify one. A recording can also include other units that keyed up during the same transmission.
  - **Talkgroups:** where the unit talks, how often and when it was last heard.
  - **Activity:** transmissions by hour of day and by day of week.
  - **Talks With:** other units heard on the same talkgroup or channel within 60 s. A dispatch console talks with almost everyone.
  - **Nearby IDs:** units numbered within 100 of this one, heard or named. Agencies often number their radios in blocks.
  - Name, status and notes can be edited at the top. ALERT WHEN HEARD adds an alert rule for the unit.
- **Unit ID Log:** new Name, Status and Recordings columns, and a filter for All units, Unnamed only, Guesses only or Confirmed only. IMPORT NAMES… reads a CSV with unit ID and name columns (headings such as Unit ID / UID / Radio ID and Name / Alias; without headings, the ID is the first column and the name the second). If an imported unit already has a different name, it asks before replacing it. EXPORT NAMES… and OPEN NAMES FILE are next to it.
- **Unit alerts** with "is exactly" now match on the unit number, so an alert keeps working after the unit is named.

## v1.1.25: Analyze, scanner menu, command console and more status indicators

A new **Tools** menu: Analyze…, Scanner Menu…, Command Console…, plus Scanner Screen… and Scanner Tools…. Each opens in its own window; sizes and positions are remembered.

**Tools → Analyze…** (`AST` / `APR`, Remote Command Specification V2.00)
- **Site:** uses the site the scanner is on (shown with system name and site index), or type a site index. Scan or hold on the trunked system first; the spec says Analyze needs scan mode so the database is loaded.
- **System Status:** signal, decode quality and activity bars (0–100), with system and site names, system/sub/site IDs, WACN, NAC, colour code, RAN, area, attenuator, number of frequencies and decode type.
- **Current Activity:** every channel of the site, updated 5 times a second: LCN, frequency, type (control channel, talkgroup, patch, I-call, encrypted…), talkgroup, unit ID, analog/digital/encrypted, system and site ID. The control channel is blue, new activity green, encrypted red, rows not updated for 5 s grey. Right-click a row to copy it or add an alert for its talkgroup.
- **Activity Log:** decoded control-channel messages with the scanner's time stamp, message and details. Saved to `~/SDS100Monitor/activity_log/activity_log_YYYY-MM-DD.csv` (with PC time, system and site; can be turned off), with a filter box and OPEN FOLDER. Needs a valid scanner clock.
- **LCN Monitor:** each LCN, its frequency and whether it is receiving.
- **LCN Finder:** a 30-cell grid showing each LCN as unknown, level 1–4, found or disabled, with the frequency being checked and the overall condition. Save the results on the scanner when it finishes.
- **START**, **PAUSE / RESUME** (`APR`) and **STOP**. The spec has no stop command, so STOP returns the scanner to scanning (`JPM,SCN_MODE`).

**Tools → Scanner Menu…** (`MNU` / `MSI` / `MSV` / `MSB`)
- **Open a menu:** main menu, Settings, Select lists to monitor, Close Call, Close Call bands, Search options, Weather, Broadcast screen; the current system's, department's, site's or channel's options (index filled in from the scanner); a custom search range or Tone-Out channel by number.
- The window shows the menu title, its items with the current choice ticked, and the current setting. **SELECT** (or double-click) chooses an item; menus that ask for text or a position get an entry box with the allowed length. **BACK** goes up a level, **EXIT MENU** leaves the menus, **REFRESH** re-reads.
- **Follow the scanner** re-reads the menu every second, so the window keeps up when keys are pressed on the scanner or in the Scanner Screen window.
- **SHOW XML** shows the scanner's last menu reply. The spec lists the menu reply's parts without showing how they fit together, so this is there to check against.
- The spec doesn't say what the first ("reserved") field of MSV/MSB should be. The program sends it blank, tries `0` if the scanner refuses, and remembers which worked.

**Tools → Command Console…**
- Type any remote command and press Enter; ↑ / ↓ recall earlier commands (the last 100 are remembered). A drop-down offers read-only commands (MDL, VER, GSI, GST, GCS, DTM, LCR, VOL, SQL, SVC, FQK, MSI, GLT…).
- The log shows → sent, ← replies (refusals in red) and ⋯ XML, with timestamps. Options: show the program's own commands, XML replies, and background status polls (off by default; they arrive several times a second). COPY, SAVE… and CLEAR.
- Commands that change things (POF power off, KEY, AVD, MSV, DTM/LCR/SVC with values, URC) ask once per session before sending. `AST,RAW_DATA_OUTPUT` is refused, because it streams binary data that would flood the connection.
- GLT lists requested from the console come back to the console, without disturbing Scanner Tools or Discovery.

**Status bar indicators: more of them, and clickable**
- Added: signal bars (0–4, as on the scanner's display), squelch open / closed, VOL and SQL levels, scan direction ▲ / ▼, backlight level, and the attenuator shown dimmed as "att" when off. Existing: ATT / G-ATT, KEY LOCK, FUNC, decode type, IFX, ALERT.
- Click an indicator for related actions: signal or decode type → Analyze System Status / Current Activity; ATT → toggle attenuator (FUNC + 4) or global attenuator (FUNC + hold 4); ▲ / ▼ → scan up or down; squelch / VOL → the volume and squelch controls; IFX → toggle IF Exchange (FUNC + 7); ALERT → Alerts or the Scanner Screen; backlight → backlight key or dimmer (FUNC + 5); FUNC → cancel FUNC.
- The status report has no GPS fields, so there's no GPS indicator.

**Testing note:** checked with simulated replies built from the spec's examples. Untested on the SDS100: everything in Analyze (in particular how System Status values arrive; the program reads them from the status report, where the spec defines them), the layout of the menu reply and the MSV/MSB reserved field, and whether Analyze stops cleanly with JPM. The console and SHOW XML are the quickest way to see the real replies if anything looks wrong.

## v1.1.24: Screen mirror, automatic reconnect, number tags and status indicators

**View → Scanner Screen…** opens a live copy of the scanner's display in its own window (size and position remembered; reopens at startup if it was open when you quit).
- Read from the scanner with `GST` (Remote Command Specification V2.00): every text line, large and small lines, highlighted (reverse) and underlined characters, and the scanner's colour mode (colour, black or white background).
- The alert LED is shown as a coloured dot under the screen. The status line says when the scanner is in a menu or direct entry, or in waterfall mode.
- Keys under the screen: SOFT 1–3, MENU, knob ◀ / PUSH / ▶, FUNC, ./NO, E/YES, AVOID and REPLAY, so you can work through the scanner's menus from the PC while watching the result.
- Update rate 4, 2 or 1 per second (default 2), and a Pause box. The screen is only requested while the window is open and not paused.
- Right-click the screen to copy its text or save it as a PNG image.
- If the scanner refuses `GST`, the window switches to `STS`, which gives the same display without the LED.

**Automatic connection** (checkboxes beside CONNECT, remembered):
- **Connect at startup** connects when the program opens.
- **Reconnect automatically** (on by default): if the cable is unplugged, the scanner is turned off or restarted, or it stops answering for 15 seconds, the program keeps trying to reconnect, waiting 5 s, then 10 s, up to 30 s between attempts. It finds the scanner again even if its port name changes (e.g. `/dev/ttyACM0` → `/dev/ttyACM1`). While waiting, the button reads **STOP RECONNECTING**.
- Pressing DISCONNECT never triggers a reconnect. A manual CONNECT that fails still shows the error dialog; automatic attempts report errors in the status bar instead, so dialogs don't pile up.
- With reconnect off, a scanner that stops answering gives a status-bar warning.

**SCANNER CONTROL → GO TO NUMBER TAG:** enter the favorites list, system and channel number tags and press GO (`JNT`), like entering a number tag on the scanner. Leave a tag as — to send it blank (the spec doesn't say whether blanks are allowed; if the scanner refuses, enter all three). The last tags are remembered.

**Status bar indicators** (from the scanner's status report): **ATT** / **G-ATT** (attenuator / global attenuator), **🔒 KEY LOCK**, **FUNC**, the digital mode being decoded (**P25**, **DMR**, **NXDN**…), **IFX** when IF Exchange is on for the current channel, and **● ALERT** in the alert LED's colour. Hover for a description. Nothing is shown when they're off.

**Testing note:** checked with simulated replies only. Untested on the SDS100: the exact `GST` reply (the spec gives no GST example; STS has one), whether `JNT` accepts blank tags, and USB port detection after a replug (it looks for Uniden's USB vendor ID, or "Uniden"/"SDS1" in the device name).

## v1.1.23: Discovery menu and Discovery controls

A new **Discovery** menu, next to History and View:

- **Discovery Control…** opens the Discovery window (its own resizable window; size and divider are remembered).
- **Load Sessions** opens the window and reads the session lists from the scanner.
- **Start Last Session: …** restarts the session you last started from this program.
- **Exit Discovery (Resume Scan)** sends the documented `JPM,SCN_MODE` resume-scan command.

**Discovery window** (commands from Remote Command Specification V2.00):

- **Sessions:** LOAD SESSIONS reads the Conventional (`GLT,CNV_DISCOV`) and Trunk (`GLT,TRN_DISCOV`) session lists, with their settings (limits, modulation, step, delay, logging, compare to database, record duration, time-out, auto store; system and site for trunk sessions). Double-click a session, or select it and press START SELECTED SESSION, to start it (`JPM,CDIS_MODE,<name>` / `JPM,TDIS_MODE,<name>`). **START BY NAME** starts a session by typing its name, in case listing doesn't work on your firmware.
- Sessions are created and changed on the scanner (MENU → Discovery). The remote commands can list and start sessions but not edit them.
- The program confirms from the scanner's status report that Discovery really started. If the scanner refuses (NG), the window lists the likely causes. The spec says the scanner won't enter Discovery while its clock is only temporarily set; SCANNER CONTROL → SET CLOCK FROM PC fixes that.
- **Current Discovery:** type, frequency range, modulation, step, frequency, system, site, talkgroup, unit ID, the scanner's hit count and past time, and signal, from the `ConventionalDiscovery` / `TrunkingDiscovery` status elements.
- **Avoid:** TEMPORARY AVOID and PERMANENT AVOID act on the most recent hit, which the button names (e.g. `TEMPORARY AVOID: 154.4300 MHz`); REMOVE AVOID undoes the last one. They send `AVD,CNV_DISCOV,<frequency>,,n` (frequency in 100 Hz units, as in the spec's AFREQ example) or `AVD,TRN_DISCOV,<TGID>,,n`. The spec doesn't allow hold, next or previous in Discovery, so those aren't offered.
- **Hits heard:** every hit since the program started: last heard, frequency, talkgroup, name, system, site, times heard, air time, the scanner's hit count and unit IDs. Filter box, EXPORT CSV…, CLEAR LIST. Right-click a hit to avoid it, hold on its frequency (conventional; this leaves Discovery), add an alert, or copy it.

**Reception history:** Discovery hits were previously not logged, because they carry no channel element. They are now logged like search hits: department **Discovery**; for conventional hits, system "Conventional Discovery" and the frequency as the channel; for trunk hits, the system name and the talkgroup name (or ID). PC audio capture, alerts and the unit ID log work for Discovery hits too. The CSV format is unchanged.

**Also fixed:** GLT list replies are now matched to whichever window asked (Scanner Tools or Discovery), and a long list's follow-up request no longer jumps ahead of replies already on the way.

**Testing note:** written from the remote command spec and checked with simulated scanner replies; not yet tried on the SDS100. Untested on hardware: the XML of the session lists (the spec gives only the field names), the exact status attributes during Discovery, and the AVD Discovery commands. If something shows up wrong, `gsi_capture.py` (option `r`) can save the scanner's reply to `GLT,CNV_DISCOV`, `GLT,TRN_DISCOV` or `GSI` during Discovery.

## v1.1.22: PC audio capture — one MP3 per transmission

Records the scanner's audio through your PC's sound input and saves each transmission as its own MP3, tagged with the reception details. Audio between transmissions is never saved.

**Setup**
- Connect the SDS100's headphone jack to the PC's line-in or a USB sound card (the SDS100's USB port carries only the serial connection, not audio).
- Install `python3-pyqt6.qtmultimedia` and `ffmpeg` if you don't have them. If either is missing, the panel says which one.
- In **SCANNER CONTROL → PC AUDIO CAPTURE**, choose the input and tick **Record each transmission**. The level meter works without a scanner connection, so you can set the scanner volume first; aim for about −12 to −3 dBFS during speech. Recording follows the scanner's volume knob, so leave it at a fixed setting.

**How transmissions are cut**
- A recording starts and ends with the same receptions that go into Reception History (one per channel or talkgroup change).
- The scanner is polled, so a transmission is noticed up to one polling interval late. **Pre-roll** (default 1.5 s) keeps the audio from just before it was noticed, so the first words aren't cut off. **Post-roll** (default 1.0 s) keeps recording briefly after it ends. When one transmission follows another directly, the first file ends where the next begins, so no audio appears in both.
- Not saved: receptions shorter than the **minimum length** (default 1 s), and recordings whose loudest moment is below the **silence level** (default −50 dBFS; e.g. encrypted calls or a cable unplugged). The panel shows why a reception was skipped.
- Settings (SETTINGS… button): pre-roll, post-roll, minimum length, MP3 bitrate (default 48k), mono, silence level.
- A transmission in progress when you close the program is saved before it exits.

**Files**
- MP3s are saved in `~/SDS100Monitor/audio/YYYY-MM-DD/`, named by start time and channel, e.g. `225412_Sheriff East Dispatch.mp3`.
- **ID3 tags:** title = time + channel, artist = system, album = department, date, genre "Scanner", and a comment with frequency, talkgroup, site, unit IDs, mode and RSSI. The same fields are also stored individually (START, END, DURATION, SYSTEM, DEPARTMENT, CHANNEL, FREQUENCY, TALKGROUP, SITE, UNIT_IDS, MODE, RSSI) as user-defined TXXX tags.
- **CSV index:** `recordings_YYYY-MM-DD.csv` in the same folder, one row per recording: Start, End, Duration (s), System, Department, Channel, Frequency, Talkgroup, Site, Unit IDs, Mode, RSSI (dBm), Audio Length (s), Audio File. Start, End and Duration match the reception history row; Audio Length includes pre- and post-roll. Unit IDs lists every unit heard during the transmission.
- The reception history CSV format is unchanged.

**Playing recordings**
- **History → Audio Recordings…** (or RECORDINGS… in the panel): choose a day, search, double-click to play in your default audio player. New recordings appear while the window is open.
- Right-click a reception in Reception History → **Play Recording**.
- While a transmission is being recorded, the status bar shows a green ● PC AUDIO (separate from the red ● REC for the scanner's own SD-card recording).

**Testing note:** the cutting, pre/post-roll, silence check, MP3 encoding, tags and CSV were tested with generated audio. Live capture from a sound card through Qt Multimedia hasn't yet been tested on Kubuntu with the scanner.

## v1.1.21: Quick Keys fix

- **Fixed: the Quick Keys tab rejected the scanner's replies as "unexpected".** Replies were cut off at 160 characters before reaching the program's features, but a quick-key reply holds 100 values (about 200 characters). Replies are now passed on whole; only the text shown in the status line is shortened. Confirmed with an `FQK` reply captured from the SDS100.

## v1.1.20: Scanner Tools, alerts, charts and unit ID log

**View → Scanner Tools…** opens a window with five tabs (commands from Remote Command Specification V2.00):

- **Lists:** LOAD FAVORITES LISTS, then expand favorites lists → systems → departments / sites → channels or talkgroups. Each level is read from the scanner when you expand it (`GLT`). Right-click any system, department, site, channel or talkgroup to **hold** on it, **temporarily avoid**, **permanently avoid** (asks first), or **remove an avoid** — not just the one currently on screen. The avoid column shows each item's current state; the list refreshes after a change.
- **Quick Keys:** favorites list, system and department quick keys as 10 × 10 grids (green = enabled, grey = disabled, blank = not assigned). Click a key to turn it on or off (`FQK` / `SQK` / `DQK`). Choose which favorites list and system the lower grids show. Favorites list names appear in tooltips once the Lists tab has loaded them.
- **Service Types:** the 30 preset and 10 custom service types as checkboxes (`SVC`). READ, change, then APPLY; ALL ON / ALL OFF.
- **Location:** read and set the scanner's latitude, longitude and range (`LCR`). The spec doesn't define the number format, so the scanner must be read first; changes are sent in the same format and read back to confirm. **Saved places** store locations by name; double-click one to send it to the scanner.
- **Alerts:** rules such as "Channel is Sheriff East Dispatch", "Talkgroup is TGID:44002", "Unit ID contains 3235996" or "Any field contains Fire". A matching reception raises a desktop notification and a sound, at most once per reception and no more often than the repeat interval you choose (default 60 s). Rules can be switched off without deleting them; the last 50 alerts are listed. Quick way to add one: right-click a reception in history → Alert When This Channel / Talkgroup Is Active, or right-click a channel in the Lists tab.

**History → Activity Charts…:** receptions by hour of day, per day (per month for long periods) and the top 15 channels/talkgroups, for the last 7, 30, 90 or 365 days or all history. Filter by system; measure by number of receptions or air time. Hover a bar for its value.

**History → Unit ID Log…:** every radio unit heard is now logged to `~/SDS100Monitor/unit_ids/unit_ids_YYYY-MM-DD.csv` (time, unit ID and name, system, site, department, channel, talkgroup, frequency) — one row each time a different unit transmits. The viewer has a **Units** summary (times heard, first/last heard, main talkgroups) and **All entries**, with a period filter and search. Double-click a unit to see all its transmissions. The reception history CSV format is unchanged.

**Notes:** Only the favorites-list XML is shown as an example in the spec, so lists below that level are read generically, and long lists sent in parts are followed automatically. If anything shows up wrong, the updated `gsi_capture.py` (option `r`) saves the scanner's exact reply to read-only commands such as `GLT,SYS,0`, `FQK` or `LCR`.

## v1.1.19: Audio, battery, recording, clock and tuning

New sections in the **SCANNER CONTROL** panel (which now scrolls), using commands from Remote Command Specification V2.00:

- **Audio:** Volume and Squelch sliders (0–15 on the SDS100). They follow the scanner, so turning its knobs moves the sliders; while you drag a slider, the scanner's reports don't move it back. A change is sent once the slider stops moving (`VOL,n` / `SQL,n`).
- **Battery:** the status bar shows charge level and state (charging, fully charged, no external power…), checked every 30 seconds with `GCS`. Hover for voltage, current and battery temperature. It turns red at 15% or below when not charging, or if the scanner reports a temperature or power fault.
- **Recording:** start/stop button (`URC`), a red ● REC indicator in the status bar while recording, and plain explanations of the scanner's error codes (SD card error, battery too low, session limit, clock lost).
- **Scanner clock:** READ CLOCK shows the scanner's time, its difference from the PC, and whether the scanner reports its clock as valid. SET CLOCK FROM PC reads the scanner's daylight-saving setting first and keeps it, sets the date and time, then reads the clock back to confirm. If the result is about an hour off, it says so.
- **Tune to frequency:** type a frequency and HOLD ON FREQUENCY, or right-click a reception in history → Hold on This Frequency (`QSH`). The spec doesn't say how QSH expects the frequency, so the program tries 100 Hz units first (the older Uniden convention), then MHz if rejected. It confirms from the scanner's report that it really went to the requested frequency, and remembers the format that worked.
- The serial reader now also accepts replies ending in a line feed (GCS replies do).

## v1.1.18: Waterfall in its own window

- **View → Waterfall…** opens the waterfall in its own window, which can be moved, resized and maximized independently of the main window. It is no longer a dockable tab, so it doesn't hide the other panels.
- The live graph is on the left and takes all extra space when the window is enlarged. The controls are in a column on the right, with a draggable divider between them.
- The window's size, position, divider and open/closed state are remembered. If it was open when you quit, it reopens at the next start.
- Graph data is only requested from the scanner while the waterfall window is open.
- The waterfall was removed from the PANEL selector and the dock tabs.

## v1.1.17: Live waterfall graph

- **Live waterfall graph.** While the scanner is in waterfall mode, the panel shows the current signal trace (top) and a scrolling waterfall (bottom), with the marker drawn in green and the lower, center and upper frequencies along the bottom.
  - The data is the scanner's own waterfall graph, requested with `GWF,1,ON`: 240 levels per frame, one frame per request (format confirmed from SDS100 captures, 2026-10-26).
  - Update rate: 4, 2 or 1 frames per second. The graph and rate settings are remembered.
  - Contrast adjusts automatically to the noise floor.
  - The history clears when the span or center frequency changes, so old rows never line up with the wrong frequencies.
- **Click-to-tune.** Hover over the graph to see the frequency; double-click to move the scanner's marker there. It is rounded to the current step and sent as keypad entry + E, the same as the marker-frequency box. Only works while waterfall mode is detected (or the override is ticked).
- **One program at a time on the serial port.** SDS100 Monitor now refuses to connect if another program already has the scanner's port open, and says which one. It also locks the port while connected. Two programs reading the scanner at once split its replies and corrupt both.

## v1.1.16: Waterfall control panel

A new **WATERFALL** panel (from v1.1.18 it opens in its own window from View → Waterfall…). Key functions come from the SDS100/SDS200 Waterfall manual, and key codes and status fields from Remote Command Specification V2.00.

- **Waterfall status:** center frequency, span, range, step, modulation, marker frequency and RF gain, read from the scanner's status report while the waterfall is on screen.
- **Start waterfall:** two ways to start it.
  - *START WATERFALL (JPM)* sends `JPM,WF_MODE,0`. The spec lists WF_MODE but marks its index "Reserve", so this is **untested**; the reply (OK or NG) shows in the panel.
  - *START (FUNC + key)* uses the documented method: assign Waterfall to a search key on the scanner (Menu → Search for → Set Search Key → Search Key n → Waterfall), pick that key, and press START.
- **Display:** SPAN (Soft Key 2), STEP (FUNC + Soft Key 1), HOLD / SWEEP (Soft Key 3), MAX HOLD (FUNC + Soft Key 2), FFT / WF SPLIT (FUNC + 9), RF GAIN (FUNC + 0), EXIT TO SCAN (Soft Key 1).
- **Marker / tuning:** step and fast tuning (knob, FUNC + knob), MARKER TO CENTER (FUNC + Soft Key 3), CONFIRM (E), and a marker-frequency box that types the frequency on the keypad and presses E. Frequencies outside SDS100 coverage are rejected before anything is sent.
- **Safety:** in scan mode the soft keys act as System / Department / Channel hold, so all controls except START are enabled only while the scanner reports waterfall mode. If detection doesn't work on your scanner, a checkbox enables them anyway.
- Waterfall detection and the status fields were confirmed against status reports captured from the SDS100 in v1.1.17.

## v1.1.15

- **Site and Unit ID in Scanner Information.** For trunked calls, the panel now shows the site (e.g. "Greenville County Simulcast") and the unit ID of the radio transmitting. If the unit has a stored name, both are shown, e.g. "Engine 12 (UID:3239937)". Both can be copied from the right-click menu. They are display-only and not written to the history CSV, so the file format is unchanged.
- **Cleanup keeps only the newest version.** The cleanup script now removes every older install, including v9, v24 and earlier 1.1.x builds, unless kept with `--keep` (see above).

## v1.1.14: search, Close Call and trunked frequencies

Based on GSI samples captured from the SDS100 on 2026-10-26.

- **Search and Close Call hits are now logged.** They were previously ignored because the scanner reports them in a `SrchFrequency` element, with no system, department or channel name. In history and statistics:
  - System = the scanner mode (e.g. "Custom Search", "Close Call Only")
  - Department = the search bank name (e.g. "Custom 3"), or "—" for Close Call
  - Channel = the frequency, so statistics show which frequencies were most active
- **Trunked receptions now record the voice frequency.** It comes from the scanner's `SiteFrequency` report; before, trunked calls were logged with "—".
- Hold, avoid and next/previous controls stay unavailable during search hits; they need a stored channel.
- The CSV format is unchanged, so existing history files and the archive browser work as before.

## v1.1.13: bug fixes

- **Command replies are no longer lost.** Replies such as `KEY,OK` that arrived together with a GSI status update were discarded, so the control and keypad panels often showed only `SENT:`. Serial data is now read strictly in arrival order.
- **Saved statistics persist across connections.** Connecting used to reset the statistics to zero, hiding the totals loaded from saved history.
- **Damaged history files no longer crash the program.** An unreadable CSV is now skipped with one warning listing the file, and the other files still load. Files with a byte-order mark now load at startup too.
- **Queued commands are sent before disconnecting.** Commands still waiting when you disconnect or close the program are now sent before the port closes. A key held from the Keypress Protocol Diagnostic is released on disconnect and on program close, not only when the diagnostic window is closed.
- **REMOVE AVOID targets the right channel.** It now removes the avoid from the channel most recently avoided with TEMPORARY AVOID, which the button names. Before, it acted on whichever channel was displayed after the scanner moved on. Both actions ask for confirmation and show the channel name.
- **Diagnostic log survives reconnecting.** The diagnostic window's reply log keeps working after a disconnect/reconnect.
- **Consistent reception durations.** The end of a reception is estimated as one polling interval after it was last seen, whether it ended normally, changed channel, or was cut off by a disconnect.

## v1.1.13: smaller improvements

- Changing the polling interval takes effect immediately while connected.
- The status bar shows the connected scanner's model and firmware (from MDL/VER), with a note if the device does not report itself as an SDS100.
- Right-click menus now work on dock tab bars created by dragging panels into new groups.
- A CSV save failure shows a dialog once per session, then status-bar messages, instead of a dialog after every reception.
- Removed unused code and an outdated long-press explanation.
- The installer refuses to run from inside its own install folder.

## Earlier changes (up to v1.1.12)

These were all labelled v1.1.12 in earlier builds; the individual version numbers were not kept.

**Live monitor and history**
- Reception statistics and history use a draggable vertical splitter; the split is saved between sessions.
- New receptions scroll history to the newest entry; refreshed statistics scroll to the top.
- History → Browse CSV archives (also from Reception History): browse and search any daily CSV or the legacy history, 250 rows per page, export matching rows. Archives are read-only.

**Appearance and right-click menus**
- Decorated dock tab headers: rounded corners, clearer active tab, hover highlights, accent underline.
- Context menus with distinct mouse-over highlighting.
- Right-click the scanner status or an information value to copy fields, hold/resume (when connected), or open history.
- Right-click dock tabs or title areas to detach/reattach, hide, show all, reset, or save the layout.
- Reception History, Statistics and Archive Browser context menus.

**Virtual keypad**
- Right-click any key for normal press, FUNC + press, FUNC + LONG PRESS where available, and a keypad reference.
- Weather Scan uses the documented `JPM,WX_MODE,NORMAL`.
- User-verified FUNC + long-press actions for 4, 8, 9, AVOID and REPLAY send `KEY,F,P` followed by `KEY,<key>,L`. Avoid and Replay long-press actions are labelled user-tested, without claiming an exact result.
- Holding AVOID without FUNC (documented in the physical manual) is not yet enabled.

**Experimental Keypress Protocol Diagnostic**
- Right-click any key → Keypress Protocol Diagnostic. Sends single manual `KEY` commands with modes P/L/H/R, with a preview, an acknowledgement checkbox and extra confirmation for L/H, a reply log, and manual release. L/H/R are not documented in the remote command spec.
- Does not modify firmware or GPS.

The serial protocol and CSV format are unchanged throughout.
