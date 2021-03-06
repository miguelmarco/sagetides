import shutil

def convert_list(f, parameters):
    """
    - f is a vectorial function f(x1, x2, ...) -> [...]

    Create two lists:

    - The first list contains the subexpressions that appear in the construction
    of the function

    - The second one contains the corresponding operation used to create each subexpression
    """
    variables = f[0].arguments()
    varpar = list(parameters) + list(variables)
    F = symbolic_expression([i(*variables) for i in f]).function(*varpar)
    lis = flatten([fast_callable(i,vars=varpar).op_list() for i in F], max_level=1)
    deflist = []
    stack = []
    const =[]
    stackcomp=[]
    detail=[]
    for i in lis:
        if i[0] == 'load_arg':
            stack.append(varpar[i[1]])
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
        if l1[i] in RR:
            l1.pop(i)
            l2.pop(i)
        else:
            i+=1



def remove_repeated(l1, l2):
    """
    rmoves the repeated elements of l1, and the elements of l2 that are in
the same
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

def code_list(l1,l2,f,pars):
    l3=[]
    var = f[0].arguments()
    for i in l2:
        oper = i[0]
        if oper in ["log", "exp", "sin", "cos"]:
            a = i[1]
            if a in var:
                l3.append((oper, 'var[{}]'.format(var.index(a))))
            elif a in pars:
                l3.append((oper, 'par[{}]'.format(pars.index(a))))
            else:
                l3.append((oper, 'link[{}]'.format(l1.index(a))))

        else:
            a=i[1]
            b=i[2]
            consta=False
            constb=False

            if a in var:
                aa = 'var[{}]'.format(var.index(a))
            elif a in l1:
                aa = 'link[{}]'.format(l1.index(a))
            elif a in pars:
                aa = 'par[{}]'.format(pars.index(a))
            else:
                consta=True
                aa = str(a)
            if b in var:
                bb = 'var[{}]'.format(var.index(b))
            elif b in l1:
                bb = 'link[{}]'.format(l1.index(b))
            elif b in pars:
                bb = 'par[{}]'.format(pars.index(b))
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

def parser_list(f, pars):
    variables = f[0].arguments()
    n = len(variables)
    l1,l2 = convert_list(f,pars)
    remove_repeated(l1,l2)
    remove_constants(l1,l2)
    l3 = code_list (l1, l2, f, pars)
    res = []


    l1 = list(variables)+l1
    indices = [l1.index(i(*variables))+n for i in f]
    for i in range (1,len(variables)):
        aux = indices[i-1]-len(variables)
        if aux < len(variables):
            res.append('double_var_t(itd, link[{}], var[{}], i);'.format(aux-1, i))
        else:
            res.append('double_var_t(itd, link[{}], var[{}], i);'.format(aux-len(variables), i))

    for i in range(len(l3)):
        el = l3[i]
        string = "double_"
        if el[0] == 'add':
            string += 'add_t(itd, ' + el[1] + ', ' + el[2] + ', link[{}], i);'.format(i)
        elif el[0] == 'add_c':
            string += 'add_t_cc(itd, ' + str(N(el[2])) + ', ' + el[1] + ', link[{}], i);'.format(i)
        elif el[0] == 'mul':
            string += 'mul_t(itd, ' + el[1] + ', ' + el[2] + ', link[{}], i);'.format(i)
        elif el[0] == 'mul_c':
            string += 'mul_t_cc(itd, ' + str(N(el[2])) + ', ' + el[1] + ', link[{}], i);'.format(i)
        elif el[0] == 'pow_c':
            string += 'pow_t_cc(itd, ' + el[1] + ', ' + str(N(el[2])) + ', link[{}], i);'.format(i)
        elif el[0] == 'div':
            string += 'div_t(itd, ' + el[2] + ', ' + el[1] + ', link[{}], i);'.format(i)
        elif el[0] == 'div_c':
            string += 'div_t_cv(itd, ' + str(N(el[2])) + ', ' + el[1] + ', link[{}], i);'.format(i)
        elif el[0] == 'log':
            string += 'log_t(itd, ' + el[1]  + ', link[{}], i);'.format(i)
        elif el[0] == 'exp':
            string += 'exp_t(itd, ' + el[1]  + ', link[{}], i);'.format(i)
        elif el[0] == 'sin':
            string += 'sin_t(itd, ' + el[1]  + ', ', + 'link[{}]'.format(i+1) + ', link[{}], i);'.format(i)
        elif el[0] == 'cos':
            string += 'cos_t(itd, ' + el[1]  + ', ', + 'link[{}]'.format(i-1) + ', link[{}], i);'.format(i)


        res.append(string)


    return res

def genCodeSeries(f,fname, par):
    code = parser_list(f, par)
    VAR = len(f[0].arguments())-1
    PAR = len(par)
    TT =  len(code)+1-VAR
    shutil.copy('seriesFileComp00.txt', fname)
    outfile = open(fname, 'a')
    outfile.write("\n\tstatic int VARIABLES = {};\n".format(VAR))
    outfile.write("\tstatic int PARAMETERS = {};\n".format(PAR))
    outfile.write("\tstatic int LINKS = {};\n".format(TT))
    outfile.write('\tstatic int   FUNCTIONS        = 0;\n')
    outfile.write('\tstatic int   POS_FUNCTIONS[1] = {0};\n')
    outfile.write('\n\tinitialize_dp_case();\n')
    outfile.write('\n\tfor(i=0;  i<=ORDER; i++) {\n')
    for i in code:
        outfile.write('\t\t'+i+'\n')

    outfile.write('\t}\n\twrite_dp_solution();\n\n')
    outfile.write('\treturn NUM_COLUMNS;\n}')
    outfile.close()



def gendriver(nvars, fname, parameter_values, fileoutput, initial_values, initial=0.0, final = 100.0,
              delta=0.5, tolrel=1e-16, tolabs=1e-16):
    shutil.copy('driverFileComp00.txt', fname)
    npar = len(parameter_values)
    outfile = open(fname, 'a')
    outfile.write('\n\tint npar = {};\n'.format(npar))
    outfile.write('\tdouble p[npar];\n')
    for i in range(npar):
        outfile.write('\tp[{}] = {};\n'.format(i,RR(parameter_values[i])))
    outfile.write('\tint nvar = 3;\n\tdouble v[nvar];\n')
    for i in range(len(initial_values)):
        outfile.write('\tv[{}] = {} ;\n'.format(i,RR(initial_values[i])))
    outfile.write('\tdouble tolrel = {} ;\n'.format(tolrel))
    outfile.write('\tdouble tolabs = {} ;\n'.format(tolabs))
    outfile.write('\tdouble tini = {};\n'.format(initial))
    outfile.write('\tdouble dt = {};\n'.format(delta))
    outfile.write('\tint nipt = {};\n'.format(floor((final-initial)/delta)))
    outfile.write('\tFILE* fd = fopen("' + fileoutput + '", "w");\n')
    outfile.write('\tdp_tides_delta(function_iteration, NULL, nvar, npar, nfun, v, p, tini, dt, nipt, tolrel, tolabs, NULL, fd);\n')
    outfile.write('\tfclose(fd);\n\treturn 0;\n}')
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






