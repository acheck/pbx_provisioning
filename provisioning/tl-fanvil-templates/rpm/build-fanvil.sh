#!/bin/bash

NAME=tl-fanvil-templates
bash ~/provisioning/$NAME/make_templates-fanvil.sh    

VER=1.0
REL=1

rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type ste"
rpmbuild -bb $NAME.spec --define "version $VER" --define "release $REL" --define "type mte"
