FUNCTION_BLOCK FB_MechanicalArm
VAR_INPUT
    ManualMode : BOOL;              // Manual mode selection
    SingleStepMode : BOOL;          // Single-step mode selection
    SingleCycleMode : BOOL;         // Single-cycle mode selection
    ContinuousMode : BOOL;          // Continuous mode selection
    EmergencyStop : BOOL;           // FALSE = emergency stop active
    Start : BOOL;                   // Start / step request
    DownButton : BOOL;              // Manual down button
    UpButton : BOOL;                // Manual up button
    LeftButton : BOOL;              // Manual left button
    RightButton : BOOL;             // Manual right button
    GripButton : BOOL;              // Manual grip button
    ReleaseButton : BOOL;           // Manual release button
    DownLimitSwitch : BOOL;         // Down-position limit
    UpLimitSwitch : BOOL;           // Up-position limit
    LeftLimitSwitch : BOOL;         // Left-position limit
    RightLimitSwitch : BOOL;        // Right-position limit
    GripLimitSwitch : BOOL;         // Grip completion feedback
    ReleaseLimitSwitch : BOOL;      // Release completion feedback
END_VAR
VAR_OUTPUT
    MoveDown : BOOL;                // Down command
    MoveUp : BOOL;                  // Up command
    MoveLeft : BOOL;                // Left command
    MoveRight : BOOL;               // Right command
    ActivateGrip : BOOL;            // Grip command
    ActivateRelease : BOOL;         // Release command
END_VAR
VAR
    startPrev : BOOL;               // Previous Start state for edge detection
    startRising : BOOL;             // Start rising edge this cycle
    autoStep : INT := 0;            // Automatic sequence step 0..7
    actionActive : BOOL;            // TRUE while an automatic action is running
    actionDone : BOOL;              // Completion flag of the current action
END_VAR
