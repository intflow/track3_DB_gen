for /R %%f in (*.wav) do (
	echo "%%f"
	sox "%%f" -r 48000 -b 16 "tmp.wav"
	del /q /f "%%f"
	echo f | xcopy "tmp.wav" "%%f"
	del /q /f "tmp.wav"
)