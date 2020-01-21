#!/bin/bash

store_name="applebees"
directory="backup_databases_directory"

declare -a databases_path=(
    "/home/administrador/$store_name/mwpos_server/data/databases"
)

now=$( date +'%Y%m%d_%H%M%S' )

echo "Please wait..."

main_backup_folder="/home/administrador/$directory/$now"
echo "Backup will be stored in: $main_backup_folder"


mkdir -p $directory
mkdir -p $main_backup_folder

cd $main_backup_folder
cp -va $databases_path $main_backup_folder

echo "Done!"
