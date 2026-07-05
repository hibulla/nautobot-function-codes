# App Overview

Nautobot Function Codes adds a lightweight operational classification layer for Nautobot devices. A Function Code can represent a reusable role or purpose such as access, distribution, core, edge, firewall, wireless, or any naming scheme your organization already uses.

!!! note
    Throughout this documentation, the terms "app" and "plugin" will be used interchangeably.

## Description

![Main Page](../media/ss_main_page_light.png#only-light)
![Main Page](../media/ss_main_page_dark.png#only-dark)

## Audience (User Personas) - Who should use this App?

This app is intended for network operations teams, platform engineers, and automation maintainers who need a consistent device-level function value for filtering, reporting, audits, or downstream automation.

## Authors and Maintainers

This plugin is created and maintained by [hibulla.com](https://www.hibulla.com). For questions or support, contact [contact@hibulla.com](mailto:contact@hibulla.com).

## Nautobot Features Used

The app adds Function Code records, Device Function Code Assignment records, Device list filtering, a Device table column, a Device detail panel, coverage reporting, CSV import/export, and two Nautobot Jobs for audit/import workflows.

### Extras

The app enables Nautobot extras for Function Code records, including custom fields, custom links, custom validators, export templates, GraphQL, relationships, and webhooks. It registers the `Audit Function Code Assignments` and `Import Function Code Assignments` jobs.
