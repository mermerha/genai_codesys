IF StopBtn OR EStop THEN
    Motor := FALSE;
ELSIF StartBtn THEN
    Motor := MissingSignal;
END_IF;
