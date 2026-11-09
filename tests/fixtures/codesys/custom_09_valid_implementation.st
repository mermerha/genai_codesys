IF reset AND NOT runCommand AND NOT emergencyStop THEN
    jamAlarm := FALSE;
END_IF;

motorRun := runCommand AND NOT emergencyStop AND NOT jamAlarm;
watchdog(IN := motorRun AND NOT sensorPulse, PT := T#2s);

IF watchdog.Q THEN
    jamAlarm := TRUE;
    motorRun := FALSE;
END_IF;
