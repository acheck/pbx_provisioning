#!/bin/bash

VENDOR=ciscospa
NAME=tl-$VENDOR-templates
bash ~/provisioning/$NAME/make_templates-$VENDOR.sh    

VER=1.0
REL=1

rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type ste"
rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type mte"
