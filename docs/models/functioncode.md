# Function Code

The Function Code model represents an operational classification for network devices, such as WAN, ACC, COR, or DIS.

## Fields

| Field | Description |
|-------|-------------|
| Name | Human-readable name (unique) |
| Slug | URL-safe unique identifier and natural key |
| Description | Optional long-form description |
| Active | Whether the code can be assigned to new devices |
| Created | Timestamp when the record was created |
| Last Updated | Timestamp when the record was last modified |

## Device Assignment

Devices are linked to Function Codes through the internal `DeviceFunctionCodeAssignment` model. Each device may have at most one Function Code assigned.

Manage assignments from the plugin UI:

- **Function Code detail → Assign Devices** to assign many devices to that Function Code
- **Function Codes → Device Assignments → Add** for the same bulk workflow with Function Code selected on the form
- **Function Codes → Device Assignments** to list, edit, bulk edit, or delete existing assignments
- **Function Code detail → Assigned Devices** panel to review current links
- **Device detail → Function Code** panel to view or update the assignment
- **Function Codes → Coverage** for assignment statistics
- **Function Codes → Import Assignments** for synchronous CSV import

The `/api/plugins/function-codes/device-assignments/` API endpoint is available for automation.

## CSV Import Format

```csv
device,function_code
switch-01,acc
switch-02,
```

Use the device name or UUID. Leave `function_code` empty to clear an assignment.
