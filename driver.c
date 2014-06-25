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
	VARS = 3 ;
	PARS = 1;
	double tolrel, tolabs, tini, tend, dt; 
	double v[VARS], p[PARS]; 
	v[0] = 0 ; 
	v[1] = 1 ; 
	v[2] = 0 ; 
	tini = 0 ;
	tend = 10 ;
	dt   = 0.0100000000000000 ;
	tolrel = 1e-16 ;
	tolabs = 1e-16 ;
	extern char ofname[20];	strcpy(ofname, "salida");
	minc_tides(v,VARS,p,PARS,tini,tend,dt,tolrel,tolabs);
	return 0; 
 }