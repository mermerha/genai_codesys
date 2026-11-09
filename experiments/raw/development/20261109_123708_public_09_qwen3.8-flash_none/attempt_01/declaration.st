FUNCTION_BLOCK FB_MovingAverage
VAR_INPUT
    cyclicExecution : BOOL;
    trigger : BOOL;
    value : LREAL;
    windowSize : INT;
    reset : BOOL;
END_VAR
VAR_OUTPUT
    average : LREAL;
    windowSizeReached : BOOL;
    error : BOOL;
    status : WORD;
END_VAR
VAR
    samples : ARRAY[1..100] OF LREAL;
    count : INT := 0;
    oldestIndex : INT := 1;
    sum : LREAL := 0.0;
    prevTrigger : BOOL := FALSE;
    risingEdge : BOOL := FALSE;
    validWindow : BOOL := FALSE;
    acceptSample : BOOL := FALSE;
END_VAR
