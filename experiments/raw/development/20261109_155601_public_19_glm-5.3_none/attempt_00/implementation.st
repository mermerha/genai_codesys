xModeManual := ManualMode;
xModeStep := SingleStepMode AND NOT xModeManual;
xModeCycle := SingleCycleMode AND NOT xModeManual AND NOT xModeStep;
xModeCont := ContinuousMode AND NOT xModeManual AND NOT xModeStep AND NOT xModeCycle;
rtrigStart(CLK := Start);
IF NOT EmergencyStop THEN
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
    xAutoActive := FALSE;
    xStepHold := FALSE;
    eStep := 0;
    RETURN;
END_IF;
IF xModeManual THEN
    xAutoActive := FALSE;
    xStepHold := FALSE;
    eStep := 0;
    MoveDown := DownButton AND NOT UpButton AND NOT DownLimitSwitch;
    MoveUp := UpButton AND NOT DownButton AND NOT UpLimitSwitch;
    MoveLeft := LeftButton AND NOT RightButton AND NOT LeftLimitSwitch;
    MoveRight := RightButton AND NOT LeftButton AND NOT RightLimitSwitch;
    ActivateGrip := GripButton AND NOT ReleaseButton AND NOT GripLimitSwitch;
    ActivateRelease := ReleaseButton AND NOT GripButton AND NOT ReleaseLimitSwitch;
ELSIF xModeStep THEN
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
    IF rtrigStart.Q AND NOT xStepHold THEN
        eStep := (eStep MOD 8) + 1;
        xStepHold := TRUE;
    END_IF;
    IF xStepHold THEN
        CASE eStep OF
            1: MoveDown := NOT DownLimitSwitch;
               IF DownLimitSwitch THEN xStepHold := FALSE; END_IF;
            2: ActivateGrip := NOT GripLimitSwitch;
               IF GripLimitSwitch THEN xStepHold := FALSE; END_IF;
            3: MoveUp := NOT UpLimitSwitch;
               IF UpLimitSwitch THEN xStepHold := FALSE; END_IF;
            4: MoveRight := NOT RightLimitSwitch;
               IF RightLimitSwitch THEN xStepHold := FALSE; END_IF;
            5: MoveDown := NOT DownLimitSwitch;
               IF DownLimitSwitch THEN xStepHold := FALSE; END_IF;
            6: ActivateRelease := NOT ReleaseLimitSwitch;
               IF ReleaseLimitSwitch THEN xStepHold := FALSE; END_IF;
            7: MoveUp := NOT UpLimitSwitch;
               IF UpLimitSwitch THEN xStepHold := FALSE; END_IF;
            8: MoveLeft := NOT LeftLimitSwitch;
               IF LeftLimitSwitch THEN xStepHold := FALSE; END_IF;
        END_CASE;
    END_IF;
ELSIF xModeCycle OR xModeCont THEN
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
    IF rtrigStart.Q AND NOT xAutoActive THEN
        xAutoActive := TRUE;
        eStep := 1;
    END_IF;
    IF xAutoActive THEN
        CASE eStep OF
            1: MoveDown := NOT DownLimitSwitch;
               IF DownLimitSwitch THEN eStep := 2; END_IF;
            2: ActivateGrip := NOT GripLimitSwitch;
               IF GripLimitSwitch THEN eStep := 3; END_IF;
            3: MoveUp := NOT UpLimitSwitch;
               IF UpLimitSwitch THEN eStep := 4; END_IF;
            4: MoveRight := NOT RightLimitSwitch;
               IF RightLimitSwitch THEN eStep := 5; END_IF;
            5: MoveDown := NOT DownLimitSwitch;
               IF DownLimitSwitch THEN eStep := 6; END_IF;
            6: ActivateRelease := NOT ReleaseLimitSwitch;
               IF ReleaseLimitSwitch THEN eStep := 7; END_IF;
            7: MoveUp := NOT UpLimitSwitch;
               IF UpLimitSwitch THEN eStep := 8; END_IF;
            8: MoveLeft := NOT LeftLimitSwitch;
               IF LeftLimitSwitch THEN
                   IF xModeCont THEN
                       eStep := 1;
                   ELSE
                       eStep := 0;
                       xAutoActive := FALSE;
                   END_IF;
               END_IF;
        END_CASE;
    END_IF;
ELSE
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
END_IF;
