#!/bin/bash

store_name="applebees"
directory="backup_logs_directory"

declare -a log_paths=(
    "/home/administrador/$store_name/mwpos_server/data/logs"
    "/home/administrador/$store_name/mwpos_server/data/bundles/pyscripts"
    "/home/administrador/$store_name/mwpos_server/data/bundles/tablemgr"
    "/home/administrador/$store_name/mwpos_server/data/bundles/new-production"
    "/home/administrador/$store_name/mwpos_server/data/bundles/ifoodtopic"
    "/home/administrador/$store_name/mwpos_server/data/bundles/remoteorder"
)

now=$( date +'%Y%m%d_%H%M%S' )

echo "Please wait..."

main_backup_folder="/home/administrador/$directory/$now"
echo "Backup will be stored in: $main_backup_folder"

test -d $directory
if [ $? == 1 ]; then
   mkdir -p $directory
fi


for path in "${log_paths[@]}"; do
    echo $path
    folder="${path##*/}"
    
    if [ $folder == "logs" ]; then
        folder="hv"
    fi
    
    backup_dir="$main_backup_folder/$folder"
    mkdir -p $backup_dir
    cd $path
    find . -name \*.log* -exec cp -p {} $backup_dir \;
done

echo "Done!"
