#!/bin/sh

SH_DIR=/tpdata/applications/shells/{{base_path}}
. $SH_DIR/app_env.sh

ps -ef|grep java|grep {{server_name}} |awk '{print "kill -9 "$2}'|sh

nohup java -server -Xdebug -Xnoagent -Djava.compiler=NONE -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address={{2000 + idx + 1}} -Xms128M -Xmx256M  -jar $APP_BASE_PATH{{ exe_file_path }} --spring.profiles.active=gzdev  --management.context-path=/itmanage   --spring.redis.host=56.50.32.189 --motan.zookeeper.host=56.50.32.189:2181 --port={{3000 + idx + 1}} >> $APP_LOGS_PATH/{{server_name}}.log 2>&1 &