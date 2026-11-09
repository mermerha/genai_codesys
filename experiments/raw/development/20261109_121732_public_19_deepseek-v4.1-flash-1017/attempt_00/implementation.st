MoveDown := FALSE;
MoveUp := FALSE;
MoveLeft := FALSE;
MoveRight := FALSE;
ActivateGrip := FALSE;
ActivateRelease := FALSE;

StartEdge := Start AND NOT StartPrev;
StartPrev := Start;

IF NOT EmergencyStop THEN
    ModeCode := 0;
    IF ManualMode THEN
        ModeCode := 1;
    ELSIF SingleStepMode THEN
        ModeCode := 2;
    ELSIF SingleCycleMode THEN
        ModeCode := 3;
    ELSIF ContinuousMode THEN
        ModeCode := 4;
    END_IF;

    ModeChanged := (ModeCode <> LastMode);
    IF ModeChanged THEN
        AutoStep := 0;
        StepActive := FALSE;
        AutoRunning := FALSE;
        LastMode := ModeCode;
    END_IF;

    CASE ModeCode OF
        1:
            MoveDown := DownButton AND NOT DownLimitSwitch;
            MoveUp := UpButton AND NOT UpLimitSwitch;
            MoveLeft := LeftButton AND NOT LeftLimitSwitch;
            MoveRight := RightButton AND NOT RightLimitSwitch;
            ActivateGrip := GripButton AND NOT GripLimitSwitch;
            ActivateRelease := ReleaseButton AND NOT ReleaseLimitSwitch;

            IF MoveDown AND MoveUp THEN
                MoveDown := FALSE;
                MoveUp := FALSE;
            END_IF;
            IF MoveLeft AND MoveRight THEN
                MoveLeft := FALSE;
                MoveRight := FALSE;
            END_IF;
            IF ActivateGrip AND ActivateRelease THEN
                ActivateGrip := FALSE;
                ActivateRelease := FALSE;
            END_IF;

        2:
            IF StartEdge AND NOT StepActive THEN
                StepActive := TRUE;
            END_IF;

            IF StepActive THEN
                CASE AutoStep OF
                    0:
                        IF DownLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 1;
                        ELSE
                            MoveDown := TRUE;
                        END_IF;
                    1:
                        IF GripLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 2;
                        ELSE
                            ActivateGrip := TRUE;
                        END_IF;
                    2:
                        IF UpLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 3;
                        ELSE
                            MoveUp := TRUE;
                        END_IF;
                    3:
                        IF RightLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 4;
                        ELSE
                            MoveRight := TRUE;
                        END_IF;
                    4:
                        IF DownLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 5;
                        ELSE
                            MoveDown := TRUE;
                        END_IF;
                    5:
                        IF ReleaseLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 6;
                        ELSE
                            ActivateRelease := TRUE;
                        END_IF;
                    6:
                        IF UpLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 7;
                        ELSE
                            MoveUp := TRUE;
                        END_IF;
                    7:
                        IF LeftLimitSwitch THEN
                            StepActive := FALSE;
                            AutoStep := 0;
                        ELSE
                            MoveLeft := TRUE;
                        END_IF;
                END_CASE;
            END_IF;

        3:
            IF StartEdge AND NOT AutoRunning THEN
                AutoRunning := TRUE;
                AutoStep := 0;
            END_IF;

            IF AutoRunning THEN
                CASE AutoStep OF
                    0:
                        IF DownLimitSwitch THEN
                            AutoStep := 1;
                        ELSE
                            MoveDown := TRUE;
                        END_IF;
                    1:
                        IF GripLimitSwitch THEN
                            AutoStep := 2;
                        ELSE
                            ActivateGrip := TRUE;
                        END_IF;
                    2:
                        IF UpLimitSwitch THEN
                            AutoStep := 3;
                        ELSE
                            MoveUp := TRUE;
                        END_IF;
                    3:
                        IF RightLimitSwitch THEN
                            AutoStep := 4;
                        ELSE
                            MoveRight := TRUE;
                        END_IF;
                    4:
                        IF DownLimitSwitch THEN
                            AutoStep := 5;
                        ELSE
                            MoveDown := TRUE;
                        END_IF;
                    5:
                        IF ReleaseLimitSwitch THEN
                            AutoStep := 6;
                        ELSE
                            ActivateRelease := TRUE;
                        END_IF;
                    6:
                        IF UpLimitSwitch THEN
                            AutoStep := 7;
                        ELSE
                            MoveUp := TRUE;
                        END_IF;
                    7:
                        IF LeftLimitSwitch THEN
                            AutoStep := 0;
                            AutoRunning := FALSE;
                        ELSE
                            MoveLeft := TRUE;
                        END_IF;
                END_CASE;
            END_IF;

        4:
            IF StartEdge AND NOT AutoRunning THEN
                AutoRunning := TRUE;
                AutoStep := 0;
            END_IF;

            IF AutoRunning THEN
                CASE AutoStep OF
                    0:
                        IF DownLimitSwitch THEN
                            AutoStep := 1;
                        ELSE
                            MoveDown := TRUE;
                        END_IF;
                    1:
                        IF GripLimitSwitch THEN
                            AutoStep := 2;
                        ELSE
                            ActivateGrip := TRUE;
                        END_IF;
                    2:
                        IF UpLimitSwitch THEN
                            AutoStep := 3;
                        ELSE
                            MoveUp := TRUE;
                        END_IF;
                    3:
                        IF RightLimitSwitch THEN
                            AutoStep := 4;
                        ELSE
                            MoveRight := TRUE;
                        END_IF;
                    4:
                        IF DownLimitSwitch THEN
                            AutoStep := 5;
                        ELSE
                            MoveDown := TRUE;
                        END_IF;
                    5:
                        IF ReleaseLimitSwitch THEN
                            AutoStep := 6;
                        ELSE
                            ActivateRelease := TRUE;
                        END_IF;
                    6:
                        IF UpLimitSwitch THEN
                            AutoStep := 7;
                        ELSE
                            MoveUp := TRUE;
                        END_IF;
                    7:
                        IF LeftLimitSwitch THEN
                            AutoStep := 0;
                        ELSE
                            MoveLeft := TRUE;
                        END_IF;
                END_CASE;
            END_IF;
    END_CASE;
END_IF;
