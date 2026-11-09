FUNCTION_BLOCK fixture_motor_start_stop
VAR_INPUT
    StartBtn : BOOL;
    StopBtn : BOOL;
    EStop : BOOL;
END_VAR
VAR_OUTPUT
    Motor : BOOL;
END_VAR
VAR
    MotorLatch : BOOL;
END_VAR
