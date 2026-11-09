IF StopBtn OR EStop THEN
    motor_state := FALSE;
ELSIF StartBtn THEN
    motor_state := TRUE;
END IF;
Motor := motor_state;
