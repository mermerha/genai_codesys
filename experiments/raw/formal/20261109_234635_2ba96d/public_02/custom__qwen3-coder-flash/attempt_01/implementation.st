IF value <> value__prev THEN
    hasChanged := TRUE;
ELSE
    hasChanged := FALSE;
END_IF;

risingBits := (value AND NOT value__prev);
fallingBits := (value__prev AND NOT value);

hasRisingEdges := risingBits <> 0;
hasFallingEdges := fallingBits <> 0;

noOfRisingBits := 0;
FOR i := 0 TO 31 DO
    IF (risingBits AND (1 << i)) <> 0 THEN
        noOfRisingBits := noOfRisingBits + 1;
    END_IF;
END_FOR;

noOfFallingBits := 0;
FOR i := 0 TO 31 DO
    IF (fallingBits AND (1 << i)) <> 0 THEN
        noOfFallingBits := noOfFallingBits + 1;
    END_IF;
END_FOR;

value__prev := value;
