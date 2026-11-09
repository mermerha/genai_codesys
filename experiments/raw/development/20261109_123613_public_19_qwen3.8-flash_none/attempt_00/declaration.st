FUNCTION_BLOCK FB_MechanicalArm
VAR_INPUT
    ManualMode : BOOL;
    SingleStepMode : BOOL;
    SingleCycleMode : BOOL;
    ContinuousMode : BOOL;
    EmergencyStop : BOOL; (* FALSE means active *)
    Start : BOOL;
    DownButton : BOOL;
    UpButton : BOOL;
    LeftButton : BOOL;
    RightButton : BOOL;
    GripButton : BOOL;
    ReleaseButton : BOOL;
    DownLimitSwitch : BOOL;
    UpLimitSwitch : BOOL;
    LeftLimitSwitch : BOOL;
    RightLimitSwitch : BOOL;
    GripLimitSwitch : BOOL;
    ReleaseLimitSwitch : BOOL;
END_VAR
VAR_OUTPUT
    MoveDown : BOOL;
    MoveUp : BOOL;
    MoveLeft : BOOL;
    MoveRight : BOOL;
    ActivateGrip : BOOL;
    ActivateRelease : BOOL;
END_VAR
VAR
    StepIndex : INT := 0;
    AutoRunning : BOOL := FALSE;
    StartRisingEdge : BOOL := FALSE;
    LastStart : BOOL := FALSE;
    ModeChanged : BOOL := FALSE;
    PrevManualMode : BOOL := FALSE;
    PrevSingleStepMode : BOOL := FALSE;
    PrevSingleCycleMode : BOOL := FALSE;
    PrevContinuousMode : BOOL := FALSE;
END_VAR
