Motor := motor_state;

IF EStop THEN
    motor_state := FALSE;
ELSIF StopBtn THEN
    motor_state := FALSE;
ELSIF StartBtn THEN
    motor_state := TRUE;
END_IF;
