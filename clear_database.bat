@echo off
for /f "delims=" %%a in ('dir /b /ad /s ^| findstr /i /e "\migrations"') do (
    for /r "%%a" %%i in (*) do (
        @findstr /m "initial" "%%i" && del "%%i"
    )
)