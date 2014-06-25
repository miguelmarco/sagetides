/****************************************************************************
	Driver file of the minc_tides program
	This file has been created by MathTIDES (2.00) June 23, 2014, 2:14

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

#include "minc_tides.h"

int main() {

	int  i, VARS, PARS; 
	VARS = 4;
	PARS = 1;
	double tolrel, tolabs, tini, tend, dt; 
	double v[VARS], p[PARS]; 


/************************************************************/
/************************************************************/
/*      INITIAL CONDITIONS, INTEGRATION TIMES, TOLERANCES    */
/*      Change *****  by numerical values if it is necesary */
/************************************************************/
/************************************************************/

/* --- INITIAL VALUES --- */
	v[0] = 4.0 ; 
	v[1] = 0.0 ; 
	v[2] = 0.0 ; 
	v[3] = 0.5 ; 

/* --- INITIAL INTEGRATION POINT --- */
	tini = 0.0 ;

/* --- ENDPOINT OF INTEGRATION   --- */
	tend = 100.0 ;

/* --- DELTA t FOR DENSE OUTPUT  --- */
	dt   = 0.5 ;

/* --- REQUIRED TOLERANCES --- */
	tolrel = 1.e-16 ;
	tolabs = 1.e-16 ;

/***********************************************************/
/***********************************************************/
/*  DENSE & COEFFICIENTS OUTPUT (file, screen or none)     */
/***********************************************************/
/***********************************************************/


/***********************************************************/
/***********************************************************/
/*       SHOW INITIAL POINT ON THE SCREEN                   */
/***********************************************************/
/***********************************************************/

/*	printf("Initial time = %25.15le, x = ", tini);
	for(i = 0; i < VARS-1; i++) printf("%24.15le,", v[i]);
	printf("%25.15le\n", v[VARS-1]);
*/
/***********************************************************/
/***********************************************************/
/*       CALL THE INTEGRATOR                               */
/***********************************************************/
/***********************************************************/

	minc_tides(v,VARS,p,PARS,tini,tend,dt,tolrel,tolabs);

/***********************************************************/
/***********************************************************/
/*       SHOW FINAL POINT ON THE SCREEN                    */
/*       SHOW ACCEPTED AND REJECTED STEPS ON THE SCREEN    */
/***********************************************************/
/***********************************************************/

/*	printf("  Final time = %25.15le, x = ", tend);
	for(i = 0; i < VARS-1; i++) printf("%24.15le,", v[i]);
	printf("%25.15le\n", v[VARS-1]);
*/
	return 0;
}




