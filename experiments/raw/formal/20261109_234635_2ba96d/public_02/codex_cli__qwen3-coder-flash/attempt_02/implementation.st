(* Initialize old value on first call *)
IF oldValue = 0 THEN
    oldValue := value;
END_IF;

(* Check for changes *)
hasChanged := value <> oldValue;

(* Detect rising edges *)
risingBits := (value AND NOT oldValue);
hasRisingEdges := risingBits <> 0;
noOfRisingBits := 0;

(* Count rising bits *)
FOR i := 0 TO 31 DO
    IF (risingBits AND (DWORD#1 << i)) <> 0 THEN
        noOfRisingBits := noOfRisingBits + 1;
    END_IF;
END_FOR;

(* Detect falling edges *)
fallingBits := (NOT value AND oldValue);
hasFallingEdges := fallingBits <> 0;
noOfFallingBits := 0;

(* Count falling bits *)
FOR i := 0 TO 31 DO
    IF (fallingBits AND (DWORD#1 << i)) <> 0 THEN
        noOfFallingBits := noOfFallingBits + 1;
    END_IF;
END_FOR;

(* Update old value *)
oldValue := value;
