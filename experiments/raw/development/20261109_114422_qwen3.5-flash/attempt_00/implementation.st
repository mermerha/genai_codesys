IF EStop OR StopBtn THEN
    MotorLatch := FALSE;
ELSIF StartBtn THEN
    MotorLatch := TRUE;
END_IF;
Motor := MotorLatch;
