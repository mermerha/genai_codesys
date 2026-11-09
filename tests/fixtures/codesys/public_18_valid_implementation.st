IF reset THEN
    elementCount := 0;
    head := 1;
    tail := 1;
    status := 16#0000;
ELSIF enqueue AND NOT previousEnqueue THEN
    IF elementCount >= 10 THEN
        status := 16#8002;
    ELSE
        buffer[tail] := item;
        tail := tail + 1;
        IF tail > 10 THEN
            tail := 1;
        END_IF;
        elementCount := elementCount + 1;
        status := 16#0000;
    END_IF;
ELSIF dequeue AND NOT previousDequeue THEN
    IF elementCount <= 0 THEN
        status := 16#8001;
    ELSE
        item := buffer[head];
        head := head + 1;
        IF head > 10 THEN
            head := 1;
        END_IF;
        elementCount := elementCount - 1;
        status := 16#0000;
    END_IF;
END_IF;

previousEnqueue := enqueue;
previousDequeue := dequeue;
