///////////////////////////////////////////////////////////////////

  Examples - README

///////////////////////////////////////////////////////////////////

To reproduce the examples shown in our paper, execute the
following commands:

1) Example in Figures 8 and 12:

  polyclip Fig8-P.poly Fig8-Q.poly Fig8-R.poly


2) Example in Figures 14:

  polyclip Fig14-P.poly Fig14-Q.poly Fig14-R.poly


3) Example in Figures 15:

  polyclip Fig15-P.poly Fig15-Q.poly Fig15-R.poly


4) Example in Figures 16:

  polyclip Fig16-P.poly Fig16-Q.poly Fig16-R.poly


5) Example in Figures 17:

  polyclip Fig17-P.poly Fig17-Q.poly Fig17-R.poly


6) Example in Figures 18:

  polyclip Fig18-P.poly Fig18-Q.poly Fig18-R.poly


7) Example in Figures 19:

  polyclip Fig19-P.poly Fig19-Q.poly Fig19-R.poly


8) Example in Figures 20:

  a) to compute the union of the 5 elementary school districts

  polyclip -union Fig20-E1.poly Fig20-E2.poly Fig20-E12.poly
  polyclip -union Fig20-E12.poly Fig20-E3.poly Fig20-E123.poly
  polyclip -union Fig20-E123.poly Fig20-E4.poly Fig20-E1234.poly
  polyclip -union Fig20-E1234.poly Fig20-E5.poly Fig20-E.poly

  -> "Fig20-E.poly" will contain the resulting polygon

  b) to compute the union of the 3 middle school districts

  polyclip -union Fig20-M1.poly Fig20-M2.poly Fig20-M12.poly
  polyclip -union Fig20-M12.poly Fig20-M3.poly Fig20-M.poly

  -> "Fig20-M.poly" will contain the resulting polygon

  c) to compute the union of the 2 high school districts

  polyclip -union Fig20-H1.poly Fig20-H2.poly Fig20-H.poly

  -> "Fig20-H.poly" will contain the resulting polygon

  d) to intersect the three union polygons

  polyclip Fig20-E.poly Fig20-M.poly Fig20-EM.poly
  polyclip Fig20-EM.poly Fig20-H.poly Fig20-R.poly

  -> "Fig20-R.poly" will contain the final result
