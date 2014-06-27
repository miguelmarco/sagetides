/****************************************************************************
	Driver file of the dp_tides program
	This file has been created by MathTIDES (2.00) June 24, 2014, 21:24

	Copyright (C) 2010 A. Abad, R. Barrio, F. Blesa, M. Rodriguez
	Grupo de Mecanica Espacial
	University of Zaragoza
	SPAIN

	http://gme.unizar.es/software/tides
	Contact: <tides@unizar.es>

	This file is part of TIDES.

	TIDES is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	TIDES is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with TIDES.  If not, see <http://www.gnu.org/licenses/>.

*****************************************************************************/

#include "dp_tides.h"
long  function_iteration(iteration_data *itd, double t, double v[], double p[], int ORDER, double *cvfd);

int main() {



	int npar = 3;
	double p[npar];
	p[0] = 10.0000000000000;
	p[1] = 28.0000000000000;
	p[2] = 2.66666666666667;
	int nvar = 3;
	double v[nvar];
	v[0] = 1.00000000000000 ;
	v[1] = 0.700000000000000 ;
	v[2] = 3.00000000000000 ;
	double tolrel = 1e-16 ;
	double tolabs = 1e-16 ;
	double tini = 0.0;
	double dt = 0.5;
	int nipt = 200;
	FILE* fd = fopen("output.txt", "w");
	dp_tides_delta(function_iteration, NULL, nvar, npar, nfun, v, p, tini, dt, nipt, tolrel, tolabs, NULL, fd);
	fclose(fd);
	return 0;
}