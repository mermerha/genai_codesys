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
    sampleCount : INT := 0;
    writeIndex : INT := 1;
    totalSum : LREAL := 0.0;
    triggerPrevious : BOOL;
    lastWindowSize : INT := 0;
END_VAR
