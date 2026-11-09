startRising := Start AND NOT startPrev; // detect Start rising edge
startPrev := Start;

// Default: all action outputs off
MoveDown := FALSE;
MoveUp := FALSE;
MoveLeft := FALSE;
MoveRight := FALSE;
ActivateGrip := FALSE;
ActivateRelease := FALSE;

// Emergency stop is active-low: outputs off, automatic sequence frozen
IF NOT EmergencyStop THEN
    RETURN;
END_IF;

IF ManualMode THEN
    // Manual mode cancels any automatic operation and resets the sequence
    actionActive := FALSE;
    autoStep := 0;
    // Each button commands only its matching action, blocked by its limit,
    // and opposing directions are mutually exclusive
    MoveDown := DownButton AND NOT UpButton AND NOT DownLimitSwitch;
    MoveUp := UpButton AND NOT DownButton AND NOT UpLimitSwitch;
    MoveLeft := LeftButton AND NOT RightButton AND NOT LeftLimitSwitch;
    MoveRight := RightButton AND NOT LeftButton AND NOT RightLimitSwitch;
    ActivateGrip := GripButton AND NOT ReleaseButton AND NOT GripLimitSwitch;
    ActivateRelease := ReleaseButton AND NOT GripButton AND NOT ReleaseLimitSwitch;
ELSIF SingleStepMode OR SingleCycleMode OR ContinuousMode THEN
    // A Start rising edge launches the next action only when idle
    IF startRising AND NOT actionActive THEN
        actionActive := TRUE;
    END_IF;

    IF actionActive THEN
        actionDone := FALSE;

        // Sequence: down, grip, up, right, down, release, up, left
        CASE autoStep OF
            0:
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            1:
                ActivateGrip := TRUE;
                IF GripLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            2:
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            3:
                MoveRight := TRUE;
                IF RightLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            4:
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            5:
                ActivateRelease := TRUE;
                IF ReleaseLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            6:
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
            7:
                MoveLeft := TRUE;
                IF LeftLimitSwitch THEN
                    actionDone := TRUE;
                END_IF;
        END_CASE;

        IF actionDone THEN
            autoStep := (autoStep + 1) MOD 8;
            IF SingleStepMode THEN
                // Wait for the next Start rising edge
                actionActive := FALSE;
            ELSIF SingleCycleMode AND (autoStep = 0) THEN
                // Full cycle finished, arm back at top-left
                actionActive := FALSE;
            ELSE
                // Continue automatically (mid-cycle or continuous mode)
                actionActive := TRUE;
            END_IF;
        END_IF;
    END_IF;
END_IF;
