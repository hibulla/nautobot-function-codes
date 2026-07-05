# v0.2 Release Notes

This document describes all new features and changes in the release `0.2`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Device-centric Function Code management: list column, detail panel, and Device list filters
- Coverage dashboard and synchronous CSV import from the plugin UI
- Nautobot Jobs for assignment audit and CSV import
- Minimum supported Python version raised to 3.12

## [v0.2.0] - 2026-07-05

### Added

- Function Code column on the Device list
- Editable Function Code panel on Device detail pages
- Coverage dashboard with assignment statistics
- Device list filter by Function Code and by whether a device has a Function Code assigned
- Synchronous CSV import UI for device assignments
- CSV template download and current assignment export from the import UI
- Bulk assignment clearing from the plugin menu
- Coverage dashboard breakdowns by device status, location, and role
- Coverage dashboard link to assignments using inactive Function Codes
- Nautobot Jobs: Audit Function Code Assignments and Import Function Code Assignments
- Validation preventing assignment of inactive Function Codes

### Changed

- Minimum supported Python version is now 3.12
- Assignment actions now use Device Function Code Assignment change permissions instead of Function Code change permissions
- Plugin debug logging is disabled by default

### Removed

- `color` field from the Function Code model

### Fixed

- Bulk edit on Device Assignments
- Job test and execution compatibility with Nautobot 3.x job variable signatures

<!-- towncrier release notes start -->
