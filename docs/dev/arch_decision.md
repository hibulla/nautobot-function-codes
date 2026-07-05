# Architecture Decision Records

Architecture decisions for this app should be recorded here when they affect data modeling, Nautobot integration points, permissions, or long-term compatibility.

Current notable decisions:

- Device assignments are stored in `DeviceFunctionCodeAssignment` rather than as a custom field so they can have their own API, permissions, validation, and UI workflows.
- Each device has at most one Function Code assignment.
- Inactive Function Codes are retained for history but are rejected for new assignments.
