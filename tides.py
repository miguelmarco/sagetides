from tempfile import mkdtemp
import shutil
import os
from sage.misc.flatten import flatten
from sage.ext.fast_callable import fast_callable
from sage.misc.lazy_import import lazy_import
lazy_import('sage.rings.semirings.non_negative_integer_semiring', 'NN')
from sage.rings.real_mpfr import RealField
from sage.misc.functional import N



def convert_list(f):
    """
    - f is a vectorial function f(x1, x2, ...) -> [...]

    Create two lists:

    - The first list contains the subexpressions that appear in the construction
    of the function

    - The second one contains the corresponding operation used to create each subexpression
    """
    variables = f[0].arguments()
    lis = flatten([fast_callable(i,vars=variables).op_list() for i in f], max_level=1)
    deflist = []
    stack = []
    const =[]
    stackcomp=[]
    detail=[]
    for i in lis:
        if i[0] == 'load_arg':
            stack.append(variables[i[1]])
        elif i[0] == 'ipow':
            if i[1] in NN:
                basis = stack[-1]
                for j in range(i[1]-1):
                    a=stack.pop(-1)
                    detail.append(('mul', a, basis))
                    stack.append(a*basis)
                    stackcomp.append(stack[-1])
            else:
                detail.append(('pow',stack[-1],i[1]))
                stack[-1]=stack[-1]**i[1]
                stackcomp.append(stack[-1])

        elif i[0] == 'load_const':
            const.append(i[1])
            stack.append(i[1])
        elif i == 'mul':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('mul', a, b))
            stack.append(a*b)
            stackcomp.append(stack[-1])

        elif i == 'div':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('div', a, b))
            stack.append(b/a)
            stackcomp.append(stack[-1])

        elif i == 'add':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('add',a,b))
            stack.append(a+b)
            stackcomp.append(stack[-1])

        elif i == 'pow':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('pow', b, a))
            stack.append(b**a)
            stackcomp.append(stack[-1])

        elif i[0] == 'py_call' and str(i[1])=='log':
            a=stack.pop(-1)
            detail.append(('log', a))
            stack.append(log(a))
            stackcomp.append(stack[-1])

        elif i[0] == 'py_call' and str(i[1])=='exp':
            a=stack.pop(-1)
            detail.append(('exp', a))
            stack.append(exp(a))
            stackcomp.append(stack[-1])

        elif i[0] == 'py_call' and str(i[1])=='sin':
            a=stack.pop(-1)
            detail.append(('sin', a))
            detail.append(('cos', a))
            stackcomp.append(sin(a))
            stackcomp.append(cos(a))
            stack.append(sin(a))

        elif i[0] == 'py_call' and str(i[1])=='cos':
            a=stack.pop(-1)
            detail.append(('sin', a))
            detail.append(('cos', a))
            stackcomp.append(sin(a))
            stackcomp.append(cos(a))
            stack.append(cos(a))

        elif i == 'neg':
            a = stack.pop(-1)
            detail.append(('mul', -1, a))
            stack.append(-a)
            stackcomp.append(-a)

    return stackcomp,detail

def remove_constants(l1,l2):
    i=0
    while i < len(l1):
        if (not l1[i] in SR) or len(l1[i].variables())==0:
            l1.pop(i)
            l2.pop(i)
        else:
            i+=1


def remove_repeat(l1, l2):
    """
    rmoves the repeated elements of l1, and the elements of l2 that are in the same
    positions.
    """
    for i in range(len(l1)-1):
        j=i+1
        while j<len(l1):
            if l1[j] == l1[i]:
                l1.pop(j)
                l2.pop(j)
            else:
                j+=1

def final_list(l1,l2,f):
    l3=[]
    var = f[0].arguments()
    for i in l2:
        oper = i[0]
        if oper in ["log", "exp", "sin", "cos"]:
            a = i[1]
            if a in var:
                l3.append((oper, 'XX[{}]'.format(var.index(a))))
            elif a in l1:
                l3.append((oper, 'XX[{}]'.format(l1.index(a)+len(var))))

        else:
            a=i[1]
            b=i[2]
            consta=False
            constb=False

            if a in var:
                aa = 'XX[{}]'.format(var.index(a))
            elif a in l1:
                aa = 'XX[{}]'.format(l1.index(a)+len(var))
            else:
                consta=True
                aa = str(a)
            if b in var:
                bb = 'XX[{}]'.format(var.index(b))
            elif b in l1:
                bb = 'XX[{}]'.format(l1.index(b)+len(var))
            else:
                constb=True
                bb = str(b)
            if consta:
                oper += '_c'
                if not oper=='div':
                    bb, aa = aa,bb
            elif constb:
                oper += '_c'
            l3.append((oper, aa, bb))

    return l3

def sage_tides(f):
    l1,l2 = convert_list(f)
    remove_repeat(l1,l2)
    remove_constants(l1,l2)
    return final_list(l1,l2,f)

def parser_list(f):
    variables = f[0].arguments()
    n = len(variables)
    l1,l2 = convert_list(f)
    remove_repeat(l1,l2)
    remove_constants(l1,l2)
    l3 = final_list (l1, l2, f)
    res = []
    for i in range(len(l3)):
        el = l3[i]
        string = "XX[{}][i] = ".format(i + n)
        if el[0] == 'add':
            string += el[1] + "[i] + " + el[2] +"[i];"
        elif el[0] == 'add_c':
            string += "(i==0)? {}+".format(N(el[2])) + el[1] + "[0] : "+ el[1]+ "[i];"
        elif el[0] == 'mul':
            string += "mul_mc("+el[1]+","+el[2]+",i);"
        elif el[0] == 'mul_c':
            string += str(N(el[2])) + "*"+ el[1] + "[i];"
        elif el[0] == 'pow_c':
            string += "pow_mc_c("+el[1]+","+str(N(el[2]))+",XX[{}], i);".format(i+n)
        elif el[0] == 'div':
            string += "div_mc_c("+el[2]+","+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'div_c':
            string += "inv_mc_c("+str(N(el[2]))+","+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'log':
            string += "log_mc("+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'exp':
            string += "exp_mc("+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'sin':
            string += "sin_mc("+el[1]+",XX[{}], i);".format(i+n+1)
        elif el[0] == 'cos':
            string += "cos_mc("+el[1]+",XX[{}], i);".format(i+n-1)


        res.append(string)

    l1 = list(variables)+l1
    indices = [l1.index(i(*variables))+n for i in f]
    for i in range (1,len(variables)):
        res.append("XX[{}][i+1] = XX[{}][i] / (i+1.0);".format(i,indices[i-1]-len(variables)))

    return res,n-1,1,len(res)

def genCodeSeries(f,fname):
    code,VAR,PAR,TT = parser_list(f)
    os.system ("cat seriesFile00.txt > " + fname)
    outfile = open(fname, 'a')
    outfile.write("\tVAR = {};\n".format(VAR))
    outfile.write("\tPAR = {};\n".format(PAR))
    outfile.write("\tTT = {};\n".format(TT))
    outfile.close()
    os.system ("cat seriesFile01.txt >> " + fname)
    outfile = open(fname, 'a')
    outfile.writelines(["\t\t"+i+"\n" for i in code])
    outfile.close()
    os.system ("cat seriesFile02.txt >> " + fname)


def gendriver(nvars, fname, fileoutput, initial_values, initial=0.0, final = 100.0,
              delta=0.5, tolrel=1e-16, tolabs=1e-16):
    os.system("cat driverFile00.txt > " + fname)
    outfile = open(fname, 'a')
    outfile.write('\n\tVARS = {} ;\n'.format(nvars-1))
    outfile.write('\tPARS = 1;\n')
    outfile.write('\tdouble tolrel, tolabs, tini, tend, dt; \n')
    outfile.write('\tdouble v[VARS], p[PARS]; \n')
    for i in range(len(initial_values)):
        outfile.write('\tv[{}] = {} ; \n'.format(i, initial_values[i]))
    outfile.write('\ttini = {} ;\n'.format(initial))
    outfile.write('\ttend = {} ;\n'.format(final))
    outfile.write('\tdt   = {} ;\n'.format(delta))
    outfile.write('\ttolrel = {} ;\n'.format(tolrel))
    outfile.write('\ttolabs = {} ;\n'.format(tolabs))
    outfile.write('\textern char ofname[500];')
    outfile.write('\tstrcpy(ofname, "'+ fileoutput +'");\n')
    outfile.write('\tminc_tides(v,VARS,p,PARS,tini,tend,dt,tolrel,tolabs);\n')
    outfile.write('\treturn 0; \n }')
    outfile.close()

def salida(f, initial_values, filename, initial = 0, final = 100.0, delta = 0.5):
    n = len(f[0].arguments())
    genCodeSeries(f, 'integrator.c')
    gendriver(n, 'driver.c', filename, initial_values, initial, final, delta)
    os.system('gcc -o runme integrator.c driver.c minc_tides.c -lm -O3')
    os.system('./runme ')
    outfile = open(filename)
    res = outfile.readlines()
    outfile.close()
    for i in range(len(res)):
        l=res[i]
        l = l.split(' ')
        l = filter(lambda a: len(a) > 2, l)
        res[i] = map(RR,l)
    return res







def desolve_mintides(f, ics, initial, final, delta,  tolrel=1e-16, tolabs=1e-16):
    r"""
    Solve numerically a system of first order differential equations using the
    taylor series integrator implemeted in mintides.

    INPUT:

    - ``f`` - symboli

    """
    # get the list of operators called
    from sage.misc.misc import SAGE_ROOT
    RR = RealField()
    variables = f[0].arguments()
    nvars = len(variables)
    lis = flatten([fast_callable(i,vars=variables).op_list() for i in f], max_level=1)
    deflist = []
    stack = []
    const =[]
    stackcomp=[]
    detail=[]
    for i in lis:
        if i[0] == 'load_arg':
            stack.append(variables[i[1]])
        elif i[0] == 'ipow':
            if i[1] in NN:
                basis = stack[-1]
                for j in range(i[1]-1):
                    a=stack.pop(-1)
                    detail.append(('mul', a, basis))
                    stack.append(a*basis)
                    stackcomp.append(stack[-1])
            else:
                detail.append(('pow',stack[-1],i[1]))
                stack[-1]=stack[-1]**i[1]
                stackcomp.append(stack[-1])

        elif i[0] == 'load_const':
            const.append(i[1])
            stack.append(i[1])
        elif i == 'mul':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('mul', a, b))
            stack.append(a*b)
            stackcomp.append(stack[-1])

        elif i == 'div':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('div', a, b))
            stack.append(b/a)
            stackcomp.append(stack[-1])

        elif i == 'add':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('add',a,b))
            stack.append(a+b)
            stackcomp.append(stack[-1])

        elif i == 'pow':
            a=stack.pop(-1)
            b=stack.pop(-1)
            detail.append(('pow', b, a))
            stack.append(b**a)
            stackcomp.append(stack[-1])

        elif i[0] == 'py_call' and str(i[1])=='log':
            a=stack.pop(-1)
            detail.append(('log', a))
            stack.append(log(a))
            stackcomp.append(stack[-1])

        elif i[0] == 'py_call' and str(i[1])=='exp':
            a=stack.pop(-1)
            detail.append(('exp', a))
            stack.append(exp(a))
            stackcomp.append(stack[-1])

        elif i[0] == 'py_call' and str(i[1])=='sin':
            a=stack.pop(-1)
            detail.append(('sin', a))
            detail.append(('cos', a))
            stackcomp.append(sin(a))
            stackcomp.append(cos(a))
            stack.append(sin(a))

        elif i[0] == 'py_call' and str(i[1])=='cos':
            a=stack.pop(-1)
            detail.append(('sin', a))
            detail.append(('cos', a))
            stackcomp.append(sin(a))
            stackcomp.append(cos(a))
            stack.append(cos(a))

        elif i == 'neg':
            a = stack.pop(-1)
            detail.append(('mul', -1, a))
            stack.append(-a)
            stackcomp.append(-a)

    l1, l2 = stackcomp, detail


    #remove the repeated expressions

    for i in range(len(l1)-1):
        j=i+1
        while j<len(l1):
            if l1[j] == l1[i]:
                l1.pop(j)
                l2.pop(j)
            else:
                j+=1

    #remove the constants

    i=0
    while i < len(l1):
        if l1[i] in RR:
            l1.pop(i)
            l2.pop(i)
        else:
            i+=1

    #generate the corresponding c lines

    l3=[]
    var = f[0].arguments()
    for i in l2:
        oper = i[0]
        if oper in ["log", "exp", "sin", "cos"]:
            a = i[1]
            if a in var:
                l3.append((oper, 'XX[{}]'.format(var.index(a))))
            elif a in l1:
                l3.append((oper, 'XX[{}]'.format(l1.index(a)+len(var))))

        else:
            a=i[1]
            b=i[2]
            consta=False
            constb=False

            if a in var:
                aa = 'XX[{}]'.format(var.index(a))
            elif a in l1:
                aa = 'XX[{}]'.format(l1.index(a)+len(var))
            else:
                consta=True
                aa = str(a)
            if b in var:
                bb = 'XX[{}]'.format(var.index(b))
            elif b in l1:
                bb = 'XX[{}]'.format(l1.index(b)+len(var))
            else:
                constb=True
                bb = str(b)
            if consta:
                oper += '_c'
                if not oper=='div':
                    bb, aa = aa,bb
            elif constb:
                oper += '_c'
            l3.append((oper, aa, bb))



    n = len(variables)
    res = []
    for i in range(len(l3)):
        el = l3[i]
        string = "XX[{}][i] = ".format(i + n)
        if el[0] == 'add':
            string += el[1] + "[i] + " + el[2] +"[i];"
        elif el[0] == 'add_c':
            string += "(i==0)? {}+".format(N(el[2])) + el[1] + "[0] : "+ el[1]+ "[i];"
        elif el[0] == 'mul':
            string += "mul_mc("+el[1]+","+el[2]+",i);"
        elif el[0] == 'mul_c':
            string += str(N(el[2])) + "*"+ el[1] + "[i];"
        elif el[0] == 'pow_c':
            string += "pow_mc_c("+el[1]+","+str(N(el[2]))+",XX[{}], i);".format(i+n)
        elif el[0] == 'div':
            string += "div_mc_c("+el[2]+","+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'div_c':
            string += "inv_mc_c("+str(N(el[2]))+","+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'log':
            string += "log_mc("+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'exp':
            string += "exp_mc("+el[1]+",XX[{}], i);".format(i+n)
        elif el[0] == 'sin':
            string += "sin_mc("+el[1]+",XX[{}], i);".format(i+n+1)
        elif el[0] == 'cos':
            string += "cos_mc("+el[1]+",XX[{}], i);".format(i+n-1)


        res.append(string)

    l1 = list(variables)+l1
    indices = [l1.index(i(*variables))+n for i in f]
    for i in range (1,len(variables)):
        res.append("XX[{}][i+1] = XX[{}][i] / (i+1.0);".format(i,indices[i-1]-len(variables)))


    code = res
    VAR = len(variables)
    PAR =0
    TT = len(res)
    tempdir = mkdtemp()
    fname = tempdir + '/integrator.c'
    shutil.copy(SAGE_ROOT+'/src/sage/calculus/tides/seriesFile00.txt', fname)
    outfile = open(fname, 'a')
    outfile.write("\tVAR = {};\n".format(VAR))
    outfile.write("\tPAR = {};\n".format(PAR))
    outfile.write("\tTT = {};\n".format(TT))
    infile = open(SAGE_ROOT+'/src/sage/calculus/tides/seriesFile01.txt')
    for i in infile:
        outfile.write(i)
    infile.close()
    outfile.writelines(["\t\t"+i+"\n" for i in code])

    infile = open(SAGE_ROOT+'/src/sage/calculus/tides/seriesFile02.txt')
    for i in infile:
        outfile.write(i)
    outfile.close()

    fname = tempdir + '/driver.c'
    fileoutput = tempdir + '/output'

    shutil.copy(SAGE_ROOT+'/src/sage/calculus/tides/driverFile00.txt', fname)
    outfile = open(fname, 'a')
    outfile.write('\n\tVARS = {} ;\n'.format(nvars-1))
    outfile.write('\tPARS = 1;\n')
    outfile.write('\tdouble tolrel, tolabs, tini, tend, dt; \n')
    outfile.write('\tdouble v[VARS], p[PARS]; \n')
    for i in range(len(ics)):
        outfile.write('\tv[{}] = {} ; \n'.format(i, ics[i]))
    outfile.write('\ttini = {} ;\n'.format(initial))
    outfile.write('\ttend = {} ;\n'.format(final))
    outfile.write('\tdt   = {} ;\n'.format(delta))
    outfile.write('\ttolrel = {} ;\n'.format(tolrel))
    outfile.write('\ttolabs = {} ;\n'.format(tolabs))
    outfile.write('\textern char ofname[500];')
    outfile.write('\tstrcpy(ofname, "'+ fileoutput +'");\n')
    outfile.write('\tminc_tides(v,VARS,p,PARS,tini,tend,dt,tolrel,tolabs);\n')
    outfile.write('\treturn 0; \n }')
    outfile.close()

    runmefile = tempdir + '/runme'


    shutil.copy(SAGE_ROOT+'/src/sage/calculus/tides/minc_tides.c', tempdir)
    shutil.copy(SAGE_ROOT+'/src/sage/calculus/tides/minc_tides.h', tempdir)

    os.system('gcc -o ' + runmefile + ' ' + tempdir + '/*.c  -lm  -O2')
    os.system(tempdir+'/runme ')
    outfile = open(fileoutput)
    res = outfile.readlines()
    outfile.close()
    for i in range(len(res)):
        l=res[i]
        l = l.split(' ')
        l = filter(lambda a: len(a) > 2, l)
        res[i] = map(RR,l)
    #shutil.rmtree(tempdir)

    return res


