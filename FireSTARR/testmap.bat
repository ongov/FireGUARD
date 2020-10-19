del /s /q C:\work\firestarr_dev\test\APK
PowerShell Measure-Command {start-process python.exe -ArgumentList 'runfire.py -d --folder test --fire APK005 -m' -Wait -NoNewWindow}
