import numpy as np
import re
from scipy.optimize import curve_fit


def fit(x, y, mod=(4, 0)):
    # 完成fit的计算操作，除了多项式拟合用的是numpy的polyfit外，其他用的都是scipy的curve_fit
    x = np.array(x)
    y = np.array(y)
    popt = []
    para_names = []
    if mod[0] == 0:
        text_func, para_names = give_text_func(mod[1][2], mod[1][1])
        exec(text_func)
        p = vars()['func']
        popt, pcov = curve_fit(p, x, y)
    elif mod[0] == 4:
        z = np.polyfit(x, y, mod[1]+1)
        p = np.poly1d(z)
    else:
        text_func, para_names = give_text_func(show_function(mod)[7:], 'x')
        exec(text_func)
        p = vars()['func']
        popt, pcov = curve_fit(p, x, y)
    return p, popt, para_names


def give_text_func(text, x_name):
    # 根据字符串形式的方程，先检测出变量，在生成一个声明func的字符串，使用exec执行便得到了func
    pattern = re.compile(r'([a-z]+\d+|[a-z]+)', re.I)
    badpattern = re.compile(r'([.][a-z]+\d+|[.][a-z]+)', re.I)
    result = pattern.findall(text)
    badresult = badpattern.findall(text)
    badresult = [i[1:] for i in badresult]
    paras = []
    text_func = "def func(" + x_name
    for i in range(len(result)):
        if result[i] != x_name and not result[i] in result[:i] and not result[i] in ['sin', 'cos', 'tan', 'exp', 'np'] and not result[i] in badresult:
            text_func += ", " + result[i]
            paras.append(result[i])
    text = text.replace('^', '**')
    text = text.replace('sin', 'np.sin')
    text = text.replace('cos', 'np.cos')
    text = text.replace('tan', 'np.tan')
    text = text.replace('exp', 'np.exp')
    text = text.replace('np.np.', 'np.')
    text_func += "): return " + text
    return text_func, paras


def give_reflect(x, y, f, para, para_names, mod, language):
    # 生成结果，可以翻译成多种语言
    words = [{"zh_CN": "系数：", "en": "Coefficients:"},
             {"zh_CN": "拟合指标：", "en": "Goodness of fit:"},
             {"zh_CN": "R方值：", "en": "R-square: "},
             {"zh_CN": "普通模型", "en": "General model"},
             {"zh_CN": "：", "en": ":"},
             {"zh_CN": "{}项指数：", "en": " Exp{}:"},
             {"zh_CN": "{}项傅里叶：", "en": " Fourier{}:"},
             {"zh_CN": "{}项高斯：", "en": " Gauss{}:"},
             {"zh_CN": "线性模型{}阶多项式：", "en": "Linear model Poly{}:"},
             {"zh_CN": "{}项幂：", "en": " Power{}:"},
             {"zh_CN": "{}{}阶有理数：", "en": " Rat{}{}:"},
             {"zh_CN": "{}项正弦：", "en": " Sin{}:"},
             {"zh_CN": "威布尔：", "en": "Weibull:"}]
    text = []
    if mod[0] == 0:
        text.append(words[3][language] + words[4][language])
        text.append("    f({}) = ".format(mod[1][1]) + mod[1][2])
    elif mod[0] == 4:
        text.append("{}".format(words[8][language]).format(mod[1] + 1))
        text.append("    " + show_function(mod))
    elif mod[0] == 6:
        text.append(words[3][language] + words[10][language].format(mod[1][0], mod[1][1]+1))
        text.append("    " + show_function(mod))
    else:
        text.append(words[3][language] + words[mod[0]+4][language].format(mod[1]+1))
        text.append("    " + show_function(mod))

    text.append("{}".format(words[0][language]))
    if mod[0] == 4:
        degree = mod[1] + 1
        for i in range(degree + 1):
            text.append("     p{} = {}".format(i + 1, f[degree - i]))
        text.append("\n{}".format(words[1][language]))
        SSE = sum([(y[i] - f(x[i])) ** 2 for i in range(len(x))])
    else:
        for i in range(len(para_names)):
            text.append("     {} = {}".format(para_names[i], para[i]))
        text.append("\n{}".format(words[1][language]))
        SSE = sum([(y[i] - f(x[i], *para)) ** 2 for i in range(len(x))])
    text.append("   SSE: {}".format(SSE))
    y_ba = np.mean(y)
    text.append("   {}{}".format(words[2][language], 1 - SSE / sum([(y[i] - y_ba) ** 2 for i in range(len(x))])))
    text.append("   RMSE: {}".format(np.sqrt(SSE / len(x))))
    return text


def show_function(mod=(4, 0)):
    # 根据拟合模式生成字符串形式的方程
    poly = "f(x) = "
    if mod[0] == 1:
        if mod[1] == 0:
            poly += "a*exp(b*x)"
        else:
            poly += "a*exp(b*x) + c*exp(d*x)"
    elif mod[0] == 2:
        n = mod[1] + 1
        poly += "a0"
        for i in range(n):
            poly += " + "
            if i==0:
                poly += "a{0}*cos(x*w) + b{0}*sin(x*w)".format(i+1)
            else:
                poly += "a{0}*cos({0}*x*w) + b{0}*sin({0}*x*w)".format(i+1)
    elif mod[0] == 3:
        for i in range(mod[1] + 1):
            poly += "a{0}*exp(-((x-b{0})/c{0})^2)".format(i+1)
            if i == mod[1]:
                break
            poly += " + "
    elif mod[0] == 4:
        n = mod[1]+1
        for i in range(n + 1):
            if n - i == 1:
                poly += "p{}*x".format(i + 1)
            elif n - i == 0:
                poly += "p{}".format(i + 1)
                break
            else:
                poly += "p{}*x^{}".format(i + 1, n - i)
            poly += " + "
    elif mod[0] == 5:
        if mod[1] == 0:
            poly += "a*x^b"
        else:
            poly += "a*x^b + c"
    elif mod[0] == 6:
        n1 = mod[1][0]
        n2 = mod[1][1]+1
        if n1==0:
            poly += "(p1) / ("
        else:
            poly += "("+show_function(mod=(4, n1-1))[7:]+") / ("
        if n2 == 1:
            poly += "x + "
        else:
            poly += "x^{} + ".format(n2)
        for i in range(1, n2 + 1):
            if n2 - i == 1:
                poly += "q{}*x".format(i)
            elif n2 - i == 0:
                poly += "q{}".format(i)
                break
            else:
                poly += "q{}*x^{}".format(i, n2 - i)
            poly += " + "
        poly += ")"
    elif mod[0] == 7:
        for i in range(mod[1] + 1):
            poly += "a{0}*sin(b{0}*x+c{0})".format(i + 1)
            if i == mod[1]:
                break
            poly += " + "
    elif mod[0] == 8:
        poly += "a*b*x^(b-1)*exp(-a*x^b)"
    return poly
