python build-version.py

mkdir "../pyinstall"
rem ERASE "../pyinstall" /S/Q
PUSHD "../pyinstall"

pyinstaller "../copy_three_dirs/main.py" --clean --name copy_three_dirs --hidden-import=PIL --onefile --version-file "../versionfile.txt"
POPD
python build-version.py ../pyinstall/dist/copy_three_dirs.exe