(* Initialize old value on first call *)
IF NOT oldValue THEN
    oldValue := value;
END_IF;

(* Check for changes *)
hasChanged := value <> oldValue;

(* Detect rising edges *)
risingBits := (value AND NOT oldValue);
hasRisingEdges := risingBits <> 0;
noOfRisingBits := BYTE#0;
FOR i := 0 TO 31 DO
    IF risingBits[i] THEN
        noOfRisingBits := noOfRisingBits + 1;
    END_IF;
END_FOR;

(* Detect falling edges *)
fallingBits := (NOT value AND oldValue);
hasFallingEdges := fallingBits <> 0;
noOfFallingBits := BYTE#0;
FOR i := 0 TO 31 DO
    IF fallingBits[i] THEN
        noOfFallingBits := noOfFallingBits + 1;
    END_IF;
END_FOR;

(* Update old value *)
oldValue := value;
