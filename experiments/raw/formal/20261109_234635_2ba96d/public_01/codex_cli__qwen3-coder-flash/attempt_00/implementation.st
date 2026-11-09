CASE state OF
    0: (* Waiting for bottle *)
        Pump_Motor := bottleSensor;
        IF bottleSensor THEN
            state := 1;
        END_IF;
        
    1: (* Cleaning *)
        Pump_Motor := TRUE;
        IF cleaningConfirmButton THEN
            state := 2;
        END_IF;
        
    2: (* Filling *)
        Pump_Motor := FALSE;
        Filling_Valve := TRUE;
        IF fillingConfirmButton THEN
            state := 3;
        END_IF;
        
    3: (* Capping *)
        Filling_Valve := FALSE;
        Capping_Machine := TRUE;
        IF cappingConfirmButton THEN
            state := 4;
        END_IF;
        
    4: (* Packaging *)
        Capping_Machine := FALSE;
        Packing_Machine := TRUE;
        IF packingConfirmButton THEN
            state := 5;
        END_IF;
        
    5: (* Completion *)
        Packing_Machine := FALSE;
        Completion_Light := TRUE;
        IF finishedButton THEN
            state := 0;
        END_IF;
        
    ELSE
        state := 0;
END_CASE;
