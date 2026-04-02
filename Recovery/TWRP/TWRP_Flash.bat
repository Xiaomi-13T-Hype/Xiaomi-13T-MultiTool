@echo off
cd /d "%~dp0"
fastboot flash vendor_boot_ab "..\..\_internal\Recovery\TWRP\recovery.img"
fastboot flash vendor_boot:recovery "..\..\_internal\Recovery\TWRP\vendor_ramdisk_recovery.cpio"
fastboot reboot
echo.
echo Window will close in 5 seconds...
timeout /t 5 /nobreak >nul
