# Summary
Example integration of an Agent in PowerShell and Windows Defender checks.

If you want to use StealthGuardian with Cobalt Strike, please import `integration/cobaltstrike/stealthguardian.cna` to your Cobalt Strike client. A new menu will show at the top which can be used to configure the connection to the `Middleware`.

# Usage
1. Download `1_register.ps1 `, `2_beacon_control.ps1`, `3_transmit_log.ps1`, `4_install_task.ps1` to your endpoint, files are available via `/agent/<filename>` and automatically have SSLVerification disabled if needed
2. Register your endpoint with `.\1_register.ps1 stealthguardian 13371`
3. Use `.\4_install_task.ps1` to automatically check for new commands and sending logs
4. In StealthGuardin go to `Agents` and assign your `Reference Beacon` to the `Agent`
5. In Cobalt Strike you can now run `stealthguardian <bid of reference beacon> shell whoami` (run `printBeacon` to get your current BeaconID or `listBeacons` to list all available Beacons.)


# Files in this Directory

You can download the required files directly from the API Server from within the `/agent/` directory. Available files are:

| Command               | Description                                                                                                                 |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| 1_register.ps1        | The registration script, which can be executed with `.\1_register.ps1 -address stealthguardian -port 45134`                 |
| 2_beacon_control.ps1  | This script is used to continuously look for new commands, such as a manual `logcheck`                                      |
| 3_transmit_log.ps1    | The script transmits logs gathered by the agent modules back to the server. Usually requires elevated context to read logs. |
| 4_install_task.ps1 | Helper script to automatically execute scripts as services. Requires elevated context.                                      |
