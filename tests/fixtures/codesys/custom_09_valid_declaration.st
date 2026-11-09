FUNCTION_BLOCK FB_JamMonitor
VAR_INPUT
    runCommand : BOOL;
    sensorPulse : BOOL;
    emergencyStop : BOOL;
    reset : BOOL;
END_VAR
VAR_OUTPUT
    motorRun : BOOL;
    jamAlarm : BOOL;
END_VAR
VAR
    watchdog : TON;
END_VAR
