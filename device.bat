
@REM @echo off
@REM echo Disconnecting old connections...
@REM adb disconnect
@REM echo Setting up connected device
@REM adb tcpip 5555
@REM echo Waiting for device to initialize
@REM timeout 3
@REM FOR /F "tokens=2" %%G IN ('adb shell ip addr show wlan0 ^|find "inet "') DO set ipfull=%%G
@REM FOR /F "tokens=1 delims=/" %%G in ("%ipfull%") DO set ip=%%G
@REM echo Connecting to device with IP %ip%...
@REM adb connect %ip%

@REM @echo off

@REM rem Set the IP address of your Android device
@REM set DEVICE_IP=192.0.0.4

@REM rem Set the port number for ADB
@REM set ADB_PORT=5555

@REM rem Set the path to the ADB executable
@REM set ADB_PATH="adb"

@REM rem Restart the ADB server
@REM %ADB_PATH% kill-server
@REM %ADB_PATH% start-server

@REM rem Connect to the Android device over Wi-Fi
@REM %ADB_PATH% connect %DEVICE_IP%:%ADB_PORT%
