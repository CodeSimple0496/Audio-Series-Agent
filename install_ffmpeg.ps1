Write-Host "Downloading ffmpeg..."
Invoke-WebRequest -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile "ffmpeg.zip"
Write-Host "Extracting..."
Expand-Archive -Path "ffmpeg.zip" -DestinationPath ".\" -Force
$ffmpegDir = (Get-ChildItem -Directory -Filter "ffmpeg-master-latest-win64-gpl*").FullName
Move-Item -Path "$ffmpegDir\bin\*" -Destination ".\" -Force
Remove-Item -Path "ffmpeg.zip"
Remove-Item -Path $ffmpegDir -Recurse -Force
Write-Host "FFmpeg installed locally! The executables (ffmpeg.exe, ffprobe.exe, ffplay.exe) are now in this folder."
