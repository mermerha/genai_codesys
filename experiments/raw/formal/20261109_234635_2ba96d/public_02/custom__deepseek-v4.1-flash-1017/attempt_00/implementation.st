risingBits := value AND NOT previousValue;
fallingBits := (NOT value) AND previousValue;
hasChanged := value <> previousValue;
hasRisingEdges := risingBits <> DWORD#0;
hasFallingEdges := fallingBits <> DWORD#0;
noOfRisingBits := USINT#0;
countBits := risingBits;
FOR i := 0 TO 31 DO
    IF (countBits AND DWORD#1) <> DWORD#0 THEN
        noOfRisingBits := noOfRisingBits + USINT#1;
    END_IF;
    countBits := countBits / DWORD#2;
END_FOR;
noOfFallingBits := USINT#0;
countBits := fallingBits;
FOR i := 0 TO 31 DO
    IF (countBits AND DWORD#1) <> DWORD#0 THEN
        noOfFallingBits := noOfFallingBits + USINT#1;
    END_IF;
    countBits := countBits / DWORD#2;
END_FOR;
previousValue := value;
