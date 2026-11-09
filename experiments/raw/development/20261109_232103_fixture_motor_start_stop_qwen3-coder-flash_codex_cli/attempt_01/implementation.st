IF EStop THEN
  Motor := FALSE;
ELSIF StopBtn THEN
  Motor := FALSE;
ELSIF StartBtn THEN
  Motor := TRUE;
ELSE
  (* 保持当前状态 *)
END_IF;
