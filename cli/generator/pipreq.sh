#!/bin/sh
FILEPATH="$1"

PARENT_DIR=`echo $FILEPATH | grep -oE "[^/]+$"`

cd $FILEPATH
for dir in ./*/ ; do
  cd "$dir"
  PYTHON=(`find ./ -maxdepth 1 -name "*.py"`)
  if [ ${#PYTHON[@]} -gt 0 ]; then
    find . -maxdepth 1 -type d \( ! -name $dir \) ! -name *.git -exec bash -c "rm -rf ./*/" \;
    find . -maxdepth 1 -type d \( ! -name $dir \) ! -name *.git -exec bash -c "pipreqs '{}' --force" \;
  fi
  cd ..
done

# find $FILEPATH -maxdepth 1 -type d \( ! -name $PARENT_DIR \) ! -name *.git -exec bash -c "cd '{}' && find . ! -name 'node_modules' -type d -exec 'rm -rf {}' && rm ./*.zip" \;
# find $FILEPATH -maxdepth 1 -type d \( ! -name $PARENT_DIR \) ! -name *.git -exec bash -c "pipreqs '{}' --force" \;
# find $FILEPATH -maxdepth 1 -type d \( ! -name $PARENT_DIR \) ! -name *.git -exec bash -c "cd '{}' && ex +g/boto*/d -cwq requirements.txt" \;
