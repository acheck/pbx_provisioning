#!/bin/bash

BASE=/home/builder/provisioning/
NAME=tl-ciscocpe-templates
BUILD=/home/builder/build/$NAME

cd $BASE/$NAME
git pull

mkdir -p $BUILD
rm -rf $BUILD/$NAME
cp -rf $BASE/$NAME $BUILD
rm -rf $BUILD/$NAME/rpm
cd $BUILD

PKG=ste
echo build $NAME-$PKG.tar.gz
rm -rf $NAME-$PKG
mkdir -p $NAME-$PKG
cp -R $NAME/* $NAME-$PKG/
rm -f $NAME-$PKG.tar.gz
tar cvfz $NAME-$PKG.tar.gz $NAME-$PKG/ >/dev/null
cp -f $NAME-$PKG.tar.gz ~/rpmbuild/SOURCES/

PKG=mte
echo build $NAME-$PKG.tar.gz
rm -rf $NAME-$PKG
mkdir -p $NAME-$PKG
cp -R $NAME/* $NAME-$PKG/
rm -f $NAME-$PKG.tar.gz
tar cvfz $NAME-$PKG.tar.gz $NAME-$PKG/ >/dev/null
cp -f $NAME-$PKG.tar.gz ~/rpmbuild/SOURCES/

