#!/bin/bash

VENDOR=snom
NAME=tl-$VENDOR-templates
bash ~/provisioning/$NAME/make_templates-$VENDOR.sh    

VER=1.2
REL=5

rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type ste"
rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type mte"
