@echo off
setlocal

where go >nul 2>nul
if errorlevel 1 (
  echo Go is not installed or not on PATH.
  exit /b 1
)

go build -ldflags="-s -w" -o todo.exe main.go
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo Build complete: todo.exe
