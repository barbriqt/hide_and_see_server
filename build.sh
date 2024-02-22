rm -rf bin

pyinstaller SERVER.py \
--distpath bin/dist \
--workpath bin/build \
--clean \
--onedir \
--specpath bin \
--name "Hide&See Server" \

cp config.ini "bin/dist/Hide&See Server"

cd bin/dist
zip -r "../Hide&See Server" "Hide&See Server"
