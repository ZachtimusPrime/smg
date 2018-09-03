#!/bin/sh
FILEPATH="$1"
NPM_COLLECT="$2/node_modules/.bin/npm-collect"
echo $FILEPATH

cd $FILEPATH
for dir in ./*/ ; do
  cd "$dir"
  pwd
  nodejs=(`find ./ -maxdepth 1 -name "*.js"`)
  if [ ! -f "package.json" ] && [ ${#nodejs[@]} -gt 0 ]; then
    echo "NODE LAMBDA: package.json does not exist."
    echo "Generating package.json..."
    if [ -d "node_modules" ]; then
      echo "Found node_modules/ directory..."
      npm init -y
      $NPM_COLLECT --new --save
    else
      echo "ERROR: Could not find node_modules/ directory in $dir."
    fi
  fi
  cd ..
done