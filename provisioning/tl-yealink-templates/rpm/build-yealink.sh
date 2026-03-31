#!/bin/bash

NAME=tl-yealink-templates
bash ~/provisioning/$NAME/make_templates-yealink.sh

VER=1.3
REL=3

rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type ste"
rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type mte"
