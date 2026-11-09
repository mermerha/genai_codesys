FUNCTION_BLOCK FB_FIFOQueue
VAR_INPUT
    enqueue : BOOL;
    dequeue : BOOL;
    reset : BOOL;
END_VAR
VAR_OUTPUT
    elementCount : DINT;
    status : WORD;
END_VAR
VAR_IN_OUT
    item : DINT;
    buffer : ARRAY[1..10] OF DINT;
END_VAR
VAR
    head : DINT := 1;
    tail : DINT := 1;
    previousEnqueue : BOOL;
    previousDequeue : BOOL;
END_VAR
