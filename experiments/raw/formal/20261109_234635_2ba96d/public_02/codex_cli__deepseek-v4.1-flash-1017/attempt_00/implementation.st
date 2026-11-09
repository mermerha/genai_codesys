hasChanged := value <> lastValue;

risingBits := value AND NOT lastValue;
fallingBits := lastValue AND NOT value;

hasRisingEdges := risingBits <> DWORD#0;
hasFallingEdges := fallingBits <> DWORD#0;

noOfRisingBits := 0;
noOfFallingBits := 0;

FOR i := 0 TO 31 DO
    IF (risingBits AND SHL(DWORD#1, i)) <> DWORD#0 THEN
        noOfRisingBits := noOfRisingBits + 1;
    END_IF;

    IF (fallingBits AND SHL(DWORD#1, i)) <> DWORD#0 THEN
        noOfFallingBits := noOfFallingBits + 1;
    END_IF;
END_FOR;

lastValue := value;
