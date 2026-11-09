FUNCTION_BLOCK MotorStartStop
    VAR_INPUT
        StartBtn : BOOL;
        StopBtn : BOOL;
        EStop : BOOL;
    END_VAR
    
    VAR_OUTPUT
        Motor : BOOL;
    END_VAR
    
    VAR
        motor_state : BOOL := FALSE;
    END_VAR
END_FUNCTION_BLOCK
