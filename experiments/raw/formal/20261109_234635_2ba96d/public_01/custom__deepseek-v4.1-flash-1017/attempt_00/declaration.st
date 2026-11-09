FUNCTION_BLOCK FB_AutomatedFillingLine
VAR_INPUT
    bottleSensor : BOOL;
    cleaningConfirmButton : BOOL;
    fillingConfirmButton : BOOL;
    cappingConfirmButton : BOOL;
    packingConfirmButton : BOOL;
    finishedButton : BOOL;
END_VAR
VAR_OUTPUT
    Pump_Motor : BOOL;
    Filling_Valve : BOOL;
    Capping_Machine : BOOL;
    Packing_Machine : BOOL;
    Completion_Light : BOOL;
END_VAR
VAR
    state : INT := 0;
    rtBottleSensor : R_TRIG;
    rtCleaningConfirm : R_TRIG;
    rtFillingConfirm : R_TRIG;
    rtCappingConfirm : R_TRIG;
    rtPackingConfirm : R_TRIG;
    rtFinished : R_TRIG;
END_VAR
