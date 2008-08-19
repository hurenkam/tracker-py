rm -rf pkg
mkdir pkg
mkdir pkg/root
mkdir pkg/root/data
mkdir pkg/root/data/tracker
mkdir pkg/root/data/tracker/gpx
mkdir pkg/root/data/tracker/maps
mkdir pkg/root/data/tracker/tracks
cp src/*.py pkg
mv pkg/main.py pkg/default.py
~/bin/ensymble.py py2sis --vendor="Mark Hurenkamp" --appname=Tracker --version=0.20 --lang=EN --extrasdir=root --verbose \
--caps=PowerMgmt+ReadDeviceData+WriteDeviceData+TrustedUI+ProtServ+SwEvent+NetworkServices+LocalServices+ReadUserData+WriteUserData+Location+SurroundingsDD+UserEnvironment \
pkg
