PROGRAM b1
  VAR
    START AT %QX0.0 : BOOL;
    STOP AT %QX0.1 : BOOL;
    RUN AT %QX0.2 : BOOL;
    piece_ready AT %QX0.3 : BOOL;
    work_finished AT %QX0.4 : BOOL;
    up_limit AT %QX0.5 : BOOL := true;
    piece_available AT %QX0.6 : BOOL;
    down_limit AT %QX0.7 : BOOL;
    lower_arm AT %QX0.8 : BOOL;
    working AT %QX0.9 : BOOL;
    finished AT %QX0.10 : BOOL;
    rise_arm AT %QX0.11 : BOOL;
  END_VAR
  VAR
    R_TRIG1 : R_TRIG;
    R_TRIG2 : R_TRIG;
    R_TRIG3 : R_TRIG;
  END_VAR

  R_TRIG1(CLK := START);
  RUN := NOT(STOP) AND (RUN OR R_TRIG1.Q);
  IF up_limit AND NOT(work_finished) AND piece_ready AND RUN THEN
    piece_available := TRUE; (*set*)
  END_IF;
  lower_arm := NOT(work_finished) AND NOT(down_limit) AND piece_available AND RUN;
  IF NOT(work_finished) AND down_limit AND piece_available AND RUN THEN
    working := TRUE; (*set*)
  END_IF;
  rise_arm := work_finished AND NOT(up_limit) AND NOT(working) AND RUN;
  R_TRIG2(CLK := finished);
  IF R_TRIG2.Q AND RUN THEN
    working := FALSE; (*reset*)
  END_IF;
  R_TRIG3(CLK := finished);
  IF R_TRIG3.Q AND RUN THEN
    work_finished := TRUE; (*set*)
  END_IF;
  IF NOT(piece_ready) AND RUN THEN
    piece_available := FALSE; (*reset*)
  END_IF;
  IF NOT(piece_ready) AND RUN THEN
    work_finished := FALSE; (*reset*)
  END_IF;
END_PROGRAM


CONFIGURATION Config0

  RESOURCE Res0 ON PLC
    TASK task0(INTERVAL := T#20ms,PRIORITY := 0);
    PROGRAM instance0 WITH task0 : b1;
  END_RESOURCE
END_CONFIGURATION
