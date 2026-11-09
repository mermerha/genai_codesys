rtBottleSensor(CLK := bottleSensor);
rtCleaningConfirm(CLK := cleaningConfirmButton);
rtFillingConfirm(CLK := fillingConfirmButton);
rtCappingConfirm(CLK := cappingConfirmButton);
rtPackingConfirm(CLK := packingConfirmButton);
rtFinished(CLK := finishedButton);

CASE state OF
    0:
        IF rtBottleSensor.Q THEN
            state := 10;
        END_IF;
    10:
        IF rtCleaningConfirm.Q THEN
            state := 20;
        END_IF;
    20:
        IF rtFillingConfirm.Q THEN
            state := 30;
        END_IF;
    30:
        IF rtCappingConfirm.Q THEN
            state := 40;
        END_IF;
    40:
        IF rtPackingConfirm.Q THEN
            state := 50;
        END_IF;
    50:
        IF rtFinished.Q THEN
            state := 0;
        END_IF;
    ELSE
        state := 0;
END_CASE;

Pump_Motor := FALSE;
Filling_Valve := FALSE;
Capping_Machine := FALSE;
Packing_Machine := FALSE;
Completion_Light := FALSE;

CASE state OF
    10:
        Pump_Motor := TRUE;
    20:
        Filling_Valve := TRUE;
    30:
        Capping_Machine := TRUE;
    40:
        Packing_Machine := TRUE;
    50:
        Completion_Light := TRUE;
END_CASE;
