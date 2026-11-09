IF bottleSensor THEN
    state := 1;
END_IF;

CASE state OF
    1:
        Pump_Motor := TRUE;
        IF cleaningConfirmButton THEN
            state := 2;
        END_IF;
    2:
        Pump_Motor := FALSE;
        Filling_Valve := TRUE;
        IF fillingConfirmButton THEN
            state := 3;
        END_IF;
    3:
        Filling_Valve := FALSE;
        Capping_Machine := TRUE;
        IF cappingConfirmButton THEN
            state := 4;
        END_IF;
    4:
        Capping_Machine := FALSE;
        Packing_Machine := TRUE;
        IF packingConfirmButton THEN
            state := 5;
        END_IF;
    5:
        Packing_Machine := FALSE;
        Completion_Light := TRUE;
        IF finishedButton THEN
            state := 0;
            Completion_Light := FALSE;
        END_IF;
    ELSE:
        Pump_Motor := FALSE;
        Filling_Valve := FALSE;
        Capping_Machine := FALSE;
        Packing_Machine := FALSE;
        Completion_Light := FALSE;
END_CASE;
