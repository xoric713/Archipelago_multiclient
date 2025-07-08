# TODO: Archipelago Multi-Client Toolkit

## Phase 0: Project Foundation - completed july 8 2025
- [x] Fork Archipelago repo
- [x] Set upstream remote for future merges
- [x] Create isolated module folder (/multiclient/)
- [x] Decide GUI framework (tkinter)
- [x] Stub out CLI/GUI entry point

---

## Phase 1: YAML Builder
- [ ] Basic UI for game/slot entry
- [ ] Support custom settings per game
- [ ] Combine games into valid multiworld YAML
- [ ] Validate YAML using Archipelago schema
- [ ] Allow saving/loading YAML templates

---

## Phase 2: Launcher + Tracker Integration
- [ ] Login to all worlds via universal tracker
- [ ] Launch associated game clients
- [ ] Optional: Launch Poptracker with correct map pack
- [ ] Logger for received items and session info
- [ ] Save session logs to file (JSON/CSV)

---

## Phase 3: Apworld Updater
- [ ] UI for GitHub apworld repo input
- [ ] List all available releases
- [ ] Compare installed version to latest release
- [ ] Download selected apworld release
- [ ] Save to correct Archipelago/games directory
- [ ] Optional: Lock apworld version per YAML config

---

## Phase 4: Testing + Packaging
- [ ] End-to-end testing on Windows/Linux/Mac
- [ ] Clean failover when features/tools are missing
- [ ] Upstream-friendly toggle/module detection
- [ ] Packaging: PyInstaller or Archipelago plugin
- [ ] Write and refine user documentation
