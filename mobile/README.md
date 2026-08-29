# Mobile App

این پوشه برای اپ Flutter کاربران Farm Net است.

در Phase 1 فقط ساختار پایه نگه داشته می‌شود. پروژه Flutter، theme، localization، routing و network client در Phase 3 ساخته می‌شوند.

## Local API connectivity

The development API URL is `http://localhost:8000/api/v1` on every Flutter
target. Chrome reaches the Windows loopback address directly. Android debug
builds automatically map device/emulator port `8000` to Windows port `8000`
with `adb reverse` after `assembleDebug`.

If an already-running real phone or emulator reports `Connection refused`, keep
the app and other targets running and repair every connected Android target:

```powershell
pwsh -File .\tool\setup_android_api_reverse.ps1
```

The command is idempotent. Verify with `adb reverse --list`. Do not hard-code a
DHCP/LAN IP in `AppConfig`; Chrome, emulators, and real phones must all remain
supported.
