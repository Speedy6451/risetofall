rm -rf "dist/rise to fall.app"
rm -rf "dist/rise to fall"
pyinstaller cli.py -y -w -n "rise to fall" --add-data="src/levels/testlevel.json:levels" --icon="src/icon.icns"
codesign --remove-signature "dist/rise to fall/Python"
codesign --remove-signature "dist/rise to fall.app/Contents/MacOS/Python"
#codesign --remove-signature "dist/fall to rise"

