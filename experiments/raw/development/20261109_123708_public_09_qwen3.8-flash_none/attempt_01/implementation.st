IF reset THEN
    count := 0;
    oldestIndex := 1;
    sum := 0.0;
    windowSizeReached := FALSE;
    average := 0.0;
END_IF;

IF (windowSize >= 1) AND (windowSize <= 100) THEN
    validWindow := TRUE;
    error := FALSE;
    status := 16#0000;
ELSE
    validWindow := FALSE;
    error := TRUE;
    status := 16#8200;
END_IF;

IF validWindow THEN
    IF cyclicExecution THEN
        acceptSample := TRUE;
    ELSE
        risingEdge := trigger AND NOT prevTrigger;
        acceptSample := risingEdge;
    END_IF;
ELSE
    acceptSample := FALSE;
END_IF;

prevTrigger := trigger;

IF acceptSample THEN
    IF count < windowSize THEN
        count := count + 1;
        samples[count] := value;
        sum := sum + value;
        
        IF count = windowSize THEN
            windowSizeReached := TRUE;
            oldestIndex := 1;
        ELSE
            windowSizeReached := FALSE;
        END_IF;
    ELSE
        sum := sum - samples[oldestIndex];
        samples[oldestIndex] := value;
        sum := sum + value;
        
        oldestIndex := oldestIndex + 1;
        IF oldestIndex > windowSize THEN
            oldestIndex := 1;
        END_IF;
        
        windowSizeReached := TRUE;
    END_IF;
    
    IF count > 0 THEN
        average := sum / count;
    ELSE
        average := 0.0;
    END_IF;
END_IF;
