BEGIN
	IF StopBtn OR EStop THEN
		lState := FALSE;
	ELSIF StartBtn THEN
		lState := TRUE;
	END_IF;

	Motor := lState;
END
