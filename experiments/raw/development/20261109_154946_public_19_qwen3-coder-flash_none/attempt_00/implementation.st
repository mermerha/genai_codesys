IF NOT EmergencyStop THEN
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
    Mode := 0;
    SequenceStep := 0;
    SequenceActive := FALSE;
    CycleComplete := FALSE;
    EXIT;
END_IF;

IF ManualMode THEN
    Mode := 1;
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
    
    IF GripButton THEN
        ActivateGrip := TRUE;
    ELSE
        ActivateGrip := FALSE;
    END_IF;
    
    IF ReleaseButton THEN
        ActivateRelease := TRUE;
    ELSE
        ActivateRelease := FALSE;
    END_IF;
ELSIF SingleStepMode OR SingleCycleMode OR ContinuousMode THEN
    Mode := 2;
    
    IF NOT LastStart AND Start THEN
        IF NOT SequenceActive THEN
            SequenceActive := TRUE;
            SequenceStep := 0;
            CycleComplete := FALSE;
        END_IF;
        
        CASE SequenceStep OF
            0:
                IF NOT DownLimitSwitch THEN
                    MoveDown := TRUE;
                    SequenceStep := 1;
                END_IF;
            1:
                IF DownLimitSwitch THEN
                    MoveDown := FALSE;
                    SequenceStep := 2;
                END_IF;
            2:
                IF NOT GripLimitSwitch THEN
                    ActivateGrip := TRUE;
                    SequenceStep := 3;
                END_IF;
            3:
                IF GripLimitSwitch THEN
                    ActivateGrip := FALSE;
                    SequenceStep := 4;
                END_IF;
            4:
                IF NOT UpLimitSwitch THEN
                    MoveUp := TRUE;
                    SequenceStep := 5;
                END_IF;
            5:
                IF UpLimitSwitch THEN
                    MoveUp := FALSE;
                    SequenceStep := 6;
                END_IF;
            6:
                IF NOT RightLimitSwitch THEN
                    MoveRight := TRUE;
                    SequenceStep := 7;
                END_IF;
            7:
                IF RightLimitSwitch THEN
                    MoveRight := FALSE;
                    SequenceStep := 8;
                END_IF;
            8:
                IF NOT DownLimitSwitch THEN
                    MoveDown := TRUE;
                    SequenceStep := 9;
                END_IF;
            9:
                IF DownLimitSwitch THEN
                    MoveDown := FALSE;
                    SequenceStep := 10;
                END_IF;
            10:
                IF NOT ReleaseLimitSwitch THEN
                    ActivateRelease := TRUE;
                    SequenceStep := 11;
                END_IF;
            11:
                IF ReleaseLimitSwitch THEN
                    ActivateRelease := FALSE;
                    SequenceStep := 12;
                END_IF;
            12:
                IF NOT UpLimitSwitch THEN
                    MoveUp := TRUE;
                    SequenceStep := 13;
                END_IF;
            13:
                IF UpLimitSwitch THEN
                    MoveUp := FALSE;
                    SequenceStep := 14;
                END_IF;
            14:
                IF NOT LeftLimitSwitch THEN
                    MoveLeft := TRUE;
                    SequenceStep := 15;
                END_IF;
            15:
                IF LeftLimitSwitch THEN
                    MoveLeft := FALSE;
                    SequenceStep := 0;
                    CycleComplete := TRUE;
                END_IF;
        END_CASE;
    END_IF;
    
    IF SingleCycleMode AND CycleComplete THEN
        SequenceActive := FALSE;
    ELSIF ContinuousMode AND CycleComplete THEN
        SequenceActive := FALSE;
    END_IF;
ELSE
    Mode := 0;
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
END_IF;

LastStart := Start;
