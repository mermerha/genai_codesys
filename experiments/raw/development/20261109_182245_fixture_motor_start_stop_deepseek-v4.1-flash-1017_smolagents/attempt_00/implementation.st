IF StopBtn OR EStop THEN
    Motor := FALSE;
ELSIF StartBtn THEN
    Motor := TRUE;
END_IF;
