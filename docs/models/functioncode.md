# Function Code

The Function Code model represents an operational classification for network devices, such as WAN, ACC, COR, or DIS.

## Fields

| Field | Description |
|-------|-------------|
| Name | Human-readable name (unique) |
| Slug | URL-safe unique identifier and natural key |
| Description | Optional long-form description |
| Color | Optional display color used in the UI |
| Active | Whether the code can be assigned to new devices |
| Created | Timestamp when the record was created |
| Last Updated | Timestamp when the record was last modified |

## Device Assignment

Devices are linked to Function Codes through the internal `DeviceFunctionCodeAssignment` model. Each device may have at most one Function Code assigned.

Manage assignments from the plugin UI:

- **Function Codes → Device Assignments** for single-record create/edit and bulk updates
- **Function Code detail → Assign Devices** to assign multiple devices at once
- **Function Code detail → Assigned Devices** panel to review current links

The `/api/plugins/function-codes/device-assignments/` API endpoint is available for automation.
