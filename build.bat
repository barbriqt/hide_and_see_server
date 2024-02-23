rmdir /s /q bin

mkdir bin

pyinstaller SERVER.py ^
--distpath bin\dist ^
--workpath bin\build ^
--clean ^
--onedir ^
--specpath bin ^
--name "Hide&See Server" 

copy config.ini "bin\dist\Hide&See Server"

