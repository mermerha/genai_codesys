IF loLevel >= hiLevel THEN
    error := TRUE;
    status := 16#8001;
ELSIF hystWindow >= (hiLevel - loLevel) THEN
    error := TRUE;
    status := 16#8002;
ELSE
    error := FALSE;
    status := 16#0000;

    IF Value > hiLevel THEN
        hiAlarm := TRUE;
    ELSIF Value < (hiLevel - hystWindow) THEN
        hiAlarm := FALSE;
    END_IF;

    IF Value < loLevel THEN
        loAlarm := TRUE;
    ELSIF Value > (loLevel + hystWindow) THEN
        loAlarm := FALSE;
    END_IF;
END_IF;
