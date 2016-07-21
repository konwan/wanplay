#!/bin/sh

session_name="luigi33"

#cd ~/Sites/within3/big_red
tmux has-session -t ${session_name}
ret=$?
if [ ${ret} -eq 0 ]; then
    echo "session exist"

else
    echo "no ${session_name} session"
    # Create the session
    tmux new -s ${session_name} -n '10.0.0.21 (luigi)' -d

# 1st window (0)
tmux send-keys -t ${session_name} '  python  /usr/local/lib/python2.7/site-packages/luigi/server.py  ' C-m

# shell (1)
tmux new-window -n '10.0.0.19 (sparkmaster)' -t ${session_name}
tmux send-keys -t ${session_name}:1 " ssh -o StrictHostKeyChecking=no root@10.0.0.19 'sh /opt/spark/sbin/start-all.sh' " C-m

  # mysql (2)
  #tmux new-window -n mysql -t ${SESSION_NAME}
  #tmux send-keys -t ${SESSION_NAME}:2 'mysql -u <username> <database>' C-m

  # server/debug log (3)
  #tmux new-window -n server -t ${SESSION_NAME}
  #tmux send-keys -t ${SESSION_NAME}:3 'bundle exec rails s' C-m
  #tmux split-window -v -t ${SESSION_NAME}:3
  #tmux send-keys -t ${SESSION_NAME}:3.1 'tail -f log/development.log | grep "DEBUG"' C-m

  # rails console (4)
  #tmux new-window -n console -t ${SESSION_NAME}
  #tmux send-keys -t ${SESSION_NAME}:4 'pry -r ./config/environment' C-m

  # Start out on the first window when we attach
  #tmux select-window -t ${SESSION_NAME}:0
fi
tmux attach -t ${session_name}
