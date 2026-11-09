(* Detect Rising Edge of Start *)
StartRisingEdge := Start AND NOT LastStart;
LastStart := Start;

(* Detect Mode Changes to reset sequence if necessary, though spec implies modes are mutually exclusive selection *)
(* If mode changes, we might want to stop current auto operation depending on interpretation. 
   Spec says: "Mutually exclusive... In single-step... wait for another Start". 
   Usually changing mode stops the current cycle/step logic. *)
IF (ManualMode <> PrevManualMode) OR (SingleStepMode <> PrevSingleStepMode) OR (SingleCycleMode <> PrevSingleCycleMode) OR (ContinuousMode <> PrevContinuousMode) THEN
    AutoRunning := FALSE;
    StepIndex := 0;
    PrevManualMode := ManualMode;
    PrevSingleStepMode := SingleStepMode;
    PrevSingleCycleMode := SingleCycleMode;
    PrevContinuousMode := ContinuousMode;
END_IF;

(* Emergency Stop Logic *)
IF NOT EmergencyStop THEN
    MoveDown := FALSE;
    MoveUp := FALSE;
    MoveLeft := FALSE;
    MoveRight := FALSE;
    ActivateGrip := FALSE;
    ActivateRelease := FALSE;
    AutoRunning := FALSE;
    StepIndex := 0;
    RETURN;
END_IF;

(* Default outputs to FALSE unless commanded *)
MoveDown := FALSE;
MoveUp := FALSE;
MoveLeft := FALSE;
MoveRight := FALSE;
ActivateGrip := FALSE;
ActivateRelease := FALSE;

(* MANUAL MODE *)
IF ManualMode THEN
    IF DownButton AND NOT DownLimitSwitch THEN
        MoveDown := TRUE;
    END_IF;
    IF UpButton AND NOT UpLimitSwitch THEN
        MoveUp := TRUE;
    END_IF;
    IF LeftButton AND NOT LeftLimitSwitch THEN
        MoveLeft := TRUE;
    END_IF;
    IF RightButton AND NOT RightLimitSwitch THEN
        MoveRight := TRUE;
    END_IF;
    IF GripButton AND NOT GripLimitSwitch THEN
        ActivateGrip := TRUE;
    END_IF;
    IF ReleaseButton AND NOT ReleaseLimitSwitch THEN
        ActivateRelease := TRUE;
    END_IF;
ELSIF SingleStepMode THEN
    (* SINGLE STEP MODE *)
    IF StartRisingEdge THEN
        AutoRunning := TRUE;
    END_IF;

    IF AutoRunning THEN
        CASE StepIndex OF
            0: (* Down *)
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    MoveDown := FALSE;
                    StepIndex := 1;
                    AutoRunning := FALSE; (* Wait for next start *)
                END_IF;
            1: (* Grip *)
                ActivateGrip := TRUE;
                IF GripLimitSwitch THEN
                    ActivateGrip := FALSE;
                    StepIndex := 2;
                    AutoRunning := FALSE;
                END_IF;
            2: (* Up *)
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    MoveUp := FALSE;
                    StepIndex := 3;
                    AutoRunning := FALSE;
                END_IF;
            3: (* Right *)
                MoveRight := TRUE;
                IF RightLimitSwitch THEN
                    MoveRight := FALSE;
                    StepIndex := 4;
                    AutoRunning := FALSE;
                END_IF;
            4: (* Down *)
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    MoveDown := FALSE;
                    StepIndex := 5;
                    AutoRunning := FALSE;
                END_IF;
            5: (* Release *)
                ActivateRelease := TRUE;
                IF ReleaseLimitSwitch THEN
                    ActivateRelease := FALSE;
                    StepIndex := 6;
                    AutoRunning := FALSE;
                END_IF;
            6: (* Up *)
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    MoveUp := FALSE;
                    StepIndex := 7;
                    AutoRunning := FALSE;
                END_IF;
            7: (* Left - Return to top-left *)
                MoveLeft := TRUE;
                IF LeftLimitSwitch THEN
                    MoveLeft := FALSE;
                    StepIndex := 0;
                    AutoRunning := FALSE;
                END_IF;
            ELSE
                StepIndex := 0;
                AutoRunning := FALSE;
        END_CASE;
    END_IF;

ELSIF SingleCycleMode THEN
    (* SINGLE CYCLE MODE *)
    IF StartRisingEdge THEN
        AutoRunning := TRUE;
        StepIndex := 0;
    END_IF;

    IF AutoRunning THEN
        CASE StepIndex OF
            0: (* Down *)
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    StepIndex := 1;
                END_IF;
            1: (* Grip *)
                ActivateGrip := TRUE;
                IF GripLimitSwitch THEN
                    StepIndex := 2;
                END_IF;
            2: (* Up *)
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    StepIndex := 3;
                END_IF;
            3: (* Right *)
                MoveRight := TRUE;
                IF RightLimitSwitch THEN
                    StepIndex := 4;
                END_IF;
            4: (* Down *)
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    StepIndex := 5;
                END_IF;
            5: (* Release *)
                ActivateRelease := TRUE;
                IF ReleaseLimitSwitch THEN
                    StepIndex := 6;
                END_IF;
            6: (* Up *)
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    StepIndex := 7;
                END_IF;
            7: (* Left *)
                MoveLeft := TRUE;
                IF LeftLimitSwitch THEN
                    AutoRunning := FALSE;
                    StepIndex := 0;
                END_IF;
            ELSE
                AutoRunning := FALSE;
                StepIndex := 0;
        END_CASE;
    END_IF;

ELSIF ContinuousMode THEN
    (* CONTINUOUS MODE *)
    IF StartRisingEdge THEN
        AutoRunning := TRUE;
    END_IF;

    IF AutoRunning THEN
        CASE StepIndex OF
            0: (* Down *)
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    StepIndex := 1;
                END_IF;
            1: (* Grip *)
                ActivateGrip := TRUE;
                IF GripLimitSwitch THEN
                    StepIndex := 2;
                END_IF;
            2: (* Up *)
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    StepIndex := 3;
                END_IF;
            3: (* Right *)
                MoveRight := TRUE;
                IF RightLimitSwitch THEN
                    StepIndex := 4;
                END_IF;
            4: (* Down *)
                MoveDown := TRUE;
                IF DownLimitSwitch THEN
                    StepIndex := 5;
                END_IF;
            5: (* Release *)
                ActivateRelease := TRUE;
                IF ReleaseLimitSwitch THEN
                    StepIndex := 6;
                END_IF;
            6: (* Up *)
                MoveUp := TRUE;
                IF UpLimitSwitch THEN
                    StepIndex := 7;
                END_IF;
            7: (* Left *)
                MoveLeft := TRUE;
                IF LeftLimitSwitch THEN
                    StepIndex := 0; (* Loop back *)
                END_IF;
            ELSE
                StepIndex := 0;
        END_CASE;
    END_IF;
END_IF;
