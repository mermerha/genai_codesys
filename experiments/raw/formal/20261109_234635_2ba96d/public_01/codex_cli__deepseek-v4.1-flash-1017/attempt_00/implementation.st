CASE iState OF
    0:
        IF bottleSensor THEN
            iState := 1;
        END_IF;
    1:
        IF cleaningConfirmButton THEN
            iState := 2;
        END_IF;
    2:
        IF fillingConfirmButton THEN
            iState := 3;
        END_IF;
    3:
        IF cappingConfirmButton THEN
            iState := 4;
        END_IF;
    4:
        IF packingConfirmButton THEN
            iState := 5;
        END_IF;
    5:
        IF finishedButton THEN
            iState := 0;
        END_IF;
END_CASE

Pump_Motor := (iState = 1);
Filling_Valve := (iState = 2);
Capping_Machine := (iState = 3);
Packing_Machine := (iState = 4);
Completion_Light := (iState = 5);
