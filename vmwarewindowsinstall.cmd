@echo off
setlocal ENABLEEXTENSIONS

if %PROCESSOR_ARCHITECTURE% == AMD64 (
    set KeyName="HKLM\SOFTWARE\Wow6432Node\VMware, Inc.\VMware Workstation"
) else (
    set KeyName="HKLM\SOFTWARE\VMware, Inc.\VMware Workstation"
)
:: delims is a TAB followed by a space
for /F "tokens=2* delims=	 " %%A in ('REG QUERY %KeyName% /v InstallPath') do set InstallPath=%%B
echo VMware is installed at: %InstallPath%

echo Stopping VMware services...
net stop VMwareHostd > NUL 2>&1
net stop VMAuthdService > NUL 2>&1
net stop VMUSBArbService > NUL 2>&1
taskkill /F /IM vmware-tray.exe > NUL 2>&1

echo Patching...
pushd %~dp0
Unlocker.exe
xcopy /F /Y ..\tools\darwin.* "%InstallPath%"
popd

echo Starting VMware services...
net start VMAuthdService > NUL 2>&1
net start VMwareHostd > NUL 2>&1

echo Finished!

