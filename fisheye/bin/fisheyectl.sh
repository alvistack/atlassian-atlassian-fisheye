#!/bin/bash

FISHEYE_HOME="/var/atlassian/application-data/fisheye"
FISHEYE_CATALINA="/opt/atlassian/fisheye"

CATALINA_PID=$FISHEYE_HOME/var/catalina.pid
CATALINA_LOG=$FISHEYE_HOME/var/log/catalina.out

mkdir -p $(dirname $CATALINA_PID)
mkdir -p $(dirname $CATALINA_LOG)

case "`uname`" in
  Darwin*) if [ -z "$JAVA_HOME" ] ; then
             JAVA_HOME=/System/Library/Frameworks/JavaVM.framework/Home
           fi
           ;;
esac

if [ -z "$FISHEYE_CATALINA" ]; then
    PRG="$0"
    FISHEYE_CATALINA=`dirname "$PRG"`/..
    # make it fully qualified
    export FISHEYE_CATALINA=`cd "$FISHEYE_CATALINA" && pwd`
fi

if [ ! -f "$FISHEYE_CATALINA/fisheyeboot.jar" ] ; then
    echo "Error: Could not find $FISHEYE_CATALINA/fisheyeboot.jar"
    exit 1
fi

if [ -z "$JAVACMD" ] ; then
  if [ -n "$JAVA_HOME"  ] ; then
    if [ -x "$JAVA_HOME/jre/sh/java" ] ; then
      # IBM's JDK on AIX uses strange locations for the executables
      JAVACMD="$JAVA_HOME/jre/sh/java"
    else
      JAVACMD="$JAVA_HOME/bin/java"
    fi
  else
    JAVACMD=`which java 2> /dev/null `
    if [ -z "$JAVACMD" ] ; then
        JAVACMD=java
    fi
  fi
fi

if [ ! -x "$JAVACMD" ] ; then
  echo "Error: JAVA_HOME is not defined correctly."
  echo "  We cannot execute $JAVACMD"
  exit 1
fi

FISHEYE_OPTS="-Dfile.encoding=UTF-8 $FISHEYE_OPTS"
FISHEYE_OPTS="-XX:+UseCGroupMemoryLimitForHeap -XX:MaxRAMFraction=1 $FISHEYE_OPTS"
FISHEYE_OPTS="-Xms2048m -Xmx2048m -XX:ReservedCodeCacheSize=512m -XX:MaxPermSize=256m -Xss512k $FISHEYE_OPTS"
FISHEYE_OPTS="-Datlassian.plugins.enable.wait=300 -XX:+UnlockExperimentalVMOptions $FISHEYE_OPTS"

FISHEYE_CMD="$JAVACMD $FISHEYE_OPTS -Dfisheye.library.path=$FISHEYE_LIBRARY_PATH -Dfisheye.inst=$FISHEYE_HOME -Djava.awt.headless=true -Djava.endorsed.dirs=$FISHEYE_CATALINA/lib/endorsed -jar $FISHEYE_CATALINA/fisheyeboot.jar"

case "$1" in
    run)
        cd $FISHEYE_HOME
        sh -c "exec $FISHEYE_CMD $@ $FISHEYE_ARGS"
        ;;
    start)
        cd $FISHEYE_HOME
        nohup sh -c "exec $FISHEYE_CMD $@ $FISHEYE_ARGS" >> $CATALINA_LOG 2>&1 &
        echo $! > "$CATALINA_PID"

        if [ $? = 0 ]; then
            echo "Starting Fisheye/Crucible... Output redirected to $CATALINA_LOG"
        else
            if [-f "$CATALINA_PID" ]; then
                rm -f "$CATALINA_PID" >/dev/null 2>&1
            fi
            echo "There was a problem starting the Fisheye/Crucible"
        fi
        ;;
    stop)
        exec $FISHEYE_CMD $@ $FISHEYE_ARGS
        rm -f "$CATALINA_PID" >/dev/null 2>&1
        ;;
esac
