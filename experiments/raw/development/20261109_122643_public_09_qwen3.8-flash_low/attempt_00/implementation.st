IF (windowSize < 1) OR (windowSize > 100) THEN
    error := TRUE;
    status := 16#8200;
ELSE
    error := FALSE;
    status := 16#0000;
END_IF;

IF reset THEN
    sampleCount := 0;
    writeIndex := 1;
    totalSum := 0.0;
    average := 0.0;
    windowSizeReached := FALSE;
    lastWindowSize := 0;
END_IF;

IF (NOT error) AND (NOT reset) THEN
    IF (windowSize <> lastWindowSize) THEN
        sampleCount := 0;
        writeIndex := 1;
        totalSum := 0.0;
        average := 0.0;
        windowSizeReached := FALSE;
    END_IF;
    lastWindowSize := windowSize;

    IF cyclicExecution OR (trigger AND NOT triggerPrevious) THEN
        IF sampleCount < windowSize THEN
            samples[writeIndex] := value;
            totalSum := totalSum + value;
            sampleCount := sampleCount + 1;
        ELSE
            totalSum := totalSum + value - samples[writeIndex];
            samples[writeIndex] := value;
        END_IF;

        writeIndex := writeIndex + 1;
        IF writeIndex > windowSize THEN
            writeIndex := 1;
        END_IF;

        IF sampleCount > 0 THEN
            average := totalSum / INT_TO_LREAL(sampleCount);
        END_IF;

        windowSizeReached := (sampleCount = windowSize);
    END_IF;
END_IF;

triggerPrevious := trigger;
