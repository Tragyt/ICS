PROGRAM program0
  VAR
    START AT %QX0.0 : BOOL;
    STOP AT %QX0.1 : BOOL;
    RUN AT %QX0.2 : BOOL;
    piece_ready AT %IX0.2 : BOOL;
    is_yellow AT %QX0.8 : BOOL;
    piece_picked AT %QX0.3 : BOOL;
    PICK AT %QX0.4 : BOOL;
    POSE_N AT %QX0.5 : BOOL;
    POSE_B AT %QX0.6 : BOOL;
    picked_yellow AT %QX0.7 : BOOL;
    MOVE_CONVEJOR AT %QX0.9 : BOOL;
    convejor_speed AT %MW0 : INT;
  END_VAR
  VAR
    R_TRIG1 : R_TRIG;
  END_VAR

  R_TRIG1(CLK := START);
  RUN := NOT(STOP) AND (RUN OR R_TRIG1.Q);
  PICK := NOT(piece_picked) AND piece_ready AND RUN;
  POSE_N := NOT(picked_yellow) AND piece_picked AND RUN;
  POSE_B := picked_yellow AND piece_picked AND RUN;
  IF is_yellow AND NOT(piece_picked) AND piece_ready AND RUN THEN
    picked_yellow := TRUE; (*set*)
  END_IF;
  IF NOT(is_yellow) AND NOT(piece_picked) AND piece_ready AND RUN THEN
    picked_yellow := FALSE; (*reset*)
  END_IF;
  MOVE_CONVEJOR := NOT(piece_ready);
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : program0;
  END_RESOURCE
END_CONFIGURATION
