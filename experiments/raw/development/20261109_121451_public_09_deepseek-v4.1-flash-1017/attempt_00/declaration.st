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
    sampleCount : INT;
    writeIndex : INT;
    sampleSum : LREAL;
    lastTrigger : BOOL;
    lastWindowSize : INT;
    accept : BOOL;
END_VAR
