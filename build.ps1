
Set-Location "X:/GIT/lapse"

Remove-Item "build" -Recurse -ErrorAction Ignore

New-Item "build" -ItemType "directory"

Copy-Item "lapse.py"