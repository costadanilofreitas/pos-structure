#!/bin/bash

store_name="applebees"
directory="backup_full_directory"

declare -a main_path=(
    "/home/administrador/$store_name"
)

now=$( date +'%Y%m%d_%H%M%S' )

echo "Please wait..."

main_folder="/home/administrador/$directory/$now"
echo "Backup will be stored in: $main_folder"

test -d $directory
if [ $? == 1 ]; then
   mkdir -p $directory
fi
mkdir -p $main_folder

cd $main_backup_folder
cp -va $main_path $main_folder

echo "Done!"
