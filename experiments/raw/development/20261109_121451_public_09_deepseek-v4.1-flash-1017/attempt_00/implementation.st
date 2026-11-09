IF (windowSize < 1) OR (windowSize > 100) THEN
    error := TRUE;
    status := 16#8200;
ELSE
    error := FALSE;
    status := 16#0000;
END_IF;

IF reset THEN
    sampleSum := 0.0;
    average := 0.0;
    sampleCount := 0;
    writeIndex := 1;
    windowSizeReached := FALSE;
    lastWindowSize := windowSize;
    lastTrigger := trigger;
ELSE
    IF error THEN
        lastTrigger := trigger;
    ELSE
        IF windowSize <> lastWindowSize THEN
            sampleSum := 0.0;
            average := 0.0;
            sampleCount := 0;
            writeIndex := 1;
            windowSizeReached := FALSE;
            lastWindowSize := windowSize;
        END_IF;

        IF cyclicExecution THEN
            accept := TRUE;
        ELSIF trigger AND NOT lastTrigger THEN
            accept := TRUE;
        ELSE
            accept := FALSE;
        END_IF;

        IF accept THEN
            IF sampleCount < windowSize THEN
                samples[writeIndex] := value;
                sampleSum := sampleSum + value;
                sampleCount := sampleCount + 1;
                writeIndex := writeIndex + 1;
                IF writeIndex > windowSize THEN
                    writeIndex := 1;
                END_IF;
            ELSE
                sampleSum := sampleSum - samples[writeIndex] + value;
                samples[writeIndex] := value;
                writeIndex := writeIndex + 1;
                IF writeIndex > windowSize THEN
                    writeIndex := 1;
                END_IF;
            END_IF;

            IF sampleCount > 0 THEN
                average := sampleSum / INT_TO_LREAL(sampleCount);
            ELSE
                average := 0.0;
            END_IF;
            windowSizeReached := (sampleCount >= windowSize);
        END_IF;
        lastTrigger := trigger;
    END_IF;
END_IF;
