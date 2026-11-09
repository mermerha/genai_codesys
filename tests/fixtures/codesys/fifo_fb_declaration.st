FUNCTION_BLOCK FifoQueueProbe
VAR_IN_OUT
    item : DINT;
    buffer : ARRAY[1..10] OF DINT;
END_VAR
VAR_OUTPUT
    ok : BOOL;
END_VAR
