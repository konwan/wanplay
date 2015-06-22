#!/bin/sh

#target_user="migo"
#if [ "$(whoami)" != "$target_user" ]; then
#  exec sudo -u "$target_user" -- "$0" "$@"
#fi
a="cindy"
target_user="migo"
#sudo -u "$target_user" ${a} <<'EOF'
#  echo ${a}
#EOF

#export my_val="nono"
#sudo su migo << 'EOF'
#    echo "${my_val}"
#EOF

if [ "$(whoami)" != "$target_user" ]; then
  exec sudo -u "$target_user" -- "$0" "$@"
fi


su - migo -c 'echo "$0" "$@"' -- "$@"
echo "The message is: $shop_id"
