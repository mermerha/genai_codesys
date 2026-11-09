IF EStop THEN
    Motor := FALSE;
ELSIF StopBtn THEN
    Motor := FALSE;
ELSIF StartBtn THEN
    Motor := TRUE;
END_IF;
