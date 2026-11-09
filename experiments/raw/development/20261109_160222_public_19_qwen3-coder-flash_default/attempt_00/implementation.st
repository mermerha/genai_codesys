ModeActive := ManualMode OR SingleStepMode OR SingleCycleMode OR ContinuousMode;
IF NOT EmergencyStop THEN
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
    SequenceStep := 0;
    IsGripping := FALSE;
    IsReleasing := FALSE;
    IsMoving := FALSE;
ELSIF ManualMode THEN
    IF DownButton AND NOT DownLimitSwitch THEN
        MoveDown := TRUE;
    ELSE
        MoveDown := FALSE;
    END_IF;
    
    IF UpButton AND NOT UpLimitSwitch THEN
        MoveUp := TRUE;
    ELSE
        MoveUp := FALSE;
    END_IF;
    
    IF LeftButton AND NOT LeftLimitSwitch THEN
        MoveLeft := TRUE;
    ELSE
        MoveLeft := FALSE;
    END_IF;
    
    IF RightButton AND NOT RightLimitSwitch THEN
        MoveRight := TRUE;
    ELSE
        MoveRight := FALSE;
    END_IF;
    
    IF GripButton AND NOT IsGripping THEN
        ActivateGrip := TRUE;
        IsGripping := TRUE;
    ELSE
        ActivateGrip := FALSE;
    END_IF;
    
    IF ReleaseButton AND NOT IsReleasing THEN
        ActivateRelease := TRUE;
        IsReleasing := TRUE;
    ELSE
        ActivateRelease := FALSE;
    END_IF;
ELSIF SingleStepMode OR SingleCycleMode OR ContinuousMode THEN
    IF NOT LastStart AND Start THEN
        CASE SequenceStep OF
            0:
                IF NOT IsMoving THEN
                    MoveDown := TRUE;
                    IsMoving := TRUE;
                ELSIF DownLimitSwitch THEN
                    MoveDown := FALSE;
                    IsMoving := FALSE;
                    SequenceStep := 1;
                END_IF;
            1:
                IF NOT IsMoving THEN
                    ActivateGrip := TRUE;
                    IsMoving := TRUE;
                    IsGripping := TRUE;
                ELSIF GripLimitSwitch THEN
                    ActivateGrip := FALSE;
                    IsMoving := FALSE;
                    IsGripping := FALSE;
                    SequenceStep := 2;
                END_IF;
            2:
                IF NOT IsMoving THEN
                    MoveUp := TRUE;
                    IsMoving := TRUE;
                ELSIF UpLimitSwitch THEN
                    MoveUp := FALSE;
                    IsMoving := FALSE;
                    SequenceStep := 3;
                END_IF;
            3:
                IF NOT IsMoving THEN
                    MoveRight := TRUE;
                    IsMoving := TRUE;
                ELSIF RightLimitSwitch THEN
                    MoveRight := FALSE;
                    IsMoving := FALSE;
                    SequenceStep := 4;
                END_IF;
            4:
                IF NOT IsMoving THEN
                    MoveDown := TRUE;
                    IsMoving := TRUE;
                ELSIF DownLimitSwitch THEN
                    MoveDown := FALSE;
                    IsMoving := FALSE;
                    SequenceStep := 5;
                END_IF;
            5:
                IF NOT IsMoving THEN
                    ActivateRelease := TRUE;
                    IsMoving := TRUE;
                    IsReleasing := TRUE;
                ELSIF ReleaseLimitSwitch THEN
                    ActivateRelease := FALSE;
                    IsMoving := FALSE;
                    IsReleasing := FALSE;
                    SequenceStep := 6;
                END_IF;
            6:
                IF NOT IsMoving THEN
                    MoveUp := TRUE;
                    IsMoving := TRUE;
                ELSIF UpLimitSwitch THEN
                    MoveUp := FALSE;
                    IsMoving := FALSE;
                    SequenceStep := 7;
                END_IF;
            7:
                IF NOT IsMoving THEN
                    MoveLeft := TRUE;
                    IsMoving := TRUE;
                ELSIF LeftLimitSwitch THEN
                    MoveLeft := FALSE;
                    IsMoving := FALSE;
                    SequenceStep := 0;
                END_IF;
        END_CASE;
        
        IF (SingleCycleMode OR ContinuousMode) AND SequenceStep = 0 THEN
            IF ContinuousMode THEN
                SequenceStep := 0;
            ELSE
                SequenceStep := -1;
            END_IF;
        END_IF;
    END_IF;
END_IF;
LastStart := Start;
