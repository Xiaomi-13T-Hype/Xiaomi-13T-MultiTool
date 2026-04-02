@echo off
cd /d "%~dp0"
fastboot flash boot_ab "..\..\..\_internal\Stock_KSU_SukiSU_Magisk\HyperOS_2_TA\HyperOS 2.0.102.0\2.0.102.0_magisk_magisk.img"
fastboot reboot
echo.
echo Window will close in 5 seconds...
timeout /t 5 /nobreak >nul
