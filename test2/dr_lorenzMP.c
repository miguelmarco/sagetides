/****************************************************************************
	Driver file of the mp_tides program
	This file has been created by MathTIDES (2.00) June 27, 2014, 2:26

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

#include "mpfr.h"
#include "mp_tides.h"
#include "lorenzMP.h"

int main() {

	int i;

/* --- SET PRECISION  ------------ */
	set_precision_digits(50);

/* --- PARAMETERS  --------------- */
	int npar = 3;
	mpfr_t p[npar];
	for(i=0; i<npar; i++) mpfr_init2(p[i], TIDES_PREC);
	mpfr_set_str(p[0], "10", 10, TIDES_RND); 
	mpfr_set_str(p[1], "28.0", 10, TIDES_RND); 
	mpfr_set_str(p[2], "2.666666666666666666666666666", 10, TIDES_RND); 

/* --- VARIABLES   --------------- */
	int nvar = 3;
	mpfr_t v[nvar];
	for(i=0; i<nvar; i++) mpfr_init2(v[i], TIDES_PREC);
	mpfr_set_str(v[0], "1.0", 10, TIDES_RND); 
	mpfr_set_str(v[1], "2.41", 10, TIDES_RND); 
	mpfr_set_str(v[2], "2.2", 10, TIDES_RND); 

/* --- NUMBER OF FUNCTIONS   ----- */
	int nfun = 0;

/* --- TOLERANCES  --------------- */
	mpfr_t tolrel, tolabs;
	mpfr_init2(tolrel, TIDES_PREC); 
	mpfr_init2(tolabs, TIDES_PREC); 
	mpfr_set_str(tolrel, "1.e-49", 10, TIDES_RND);
	mpfr_set_str(tolabs, "1.e-49", 10, TIDES_RND);

/* --- INTEGRATION POINTS   ------ */
	mpfr_t tini, dt; 
	mpfr_init2(tini, TIDES_PREC); 
	mpfr_init2(dt, TIDES_PREC); 
	mpfr_set_str(tini, "0.0", 10, TIDES_RND);
	mpfr_set_str(dt, "0.001", 10, TIDES_RND);
	int  nipt  = 8000;

/* --- OUTPUT  ------------------- */

/* --- INTEGRATOR  --------------- */
	mp_tides_delta(lorenzMP, NULL, nvar, npar, nfun, v, p, tini, dt, nipt, tolrel, tolabs, NULL, stdout);

/* --- END  ---------------------- */
	return 0;
}


