from django.shortcuts import render, redirect
from .models import *

from sklearn.linear_model import LinearRegression
from statistics import mean
import scipy.optimize as optimize

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

import base64
from io import BytesIO

import pickle

def home(request):
    return render(request, 'data-input.html')


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph




# no. of products
n = 5
# no. of factors to be considered
m = 5
# prices of products
p = [10,6,17,7,20]
# Initial quantity of products
N = [50,50,50,50,50]
# discounts imposed on each product
d = [0,0,0,0,0]
# weight of the factors
f = [0,0,0,0,0]
# month
month = "jan"
# product revenues
Rp = []

sold = [[10, 12, 12, 13, 15, 18], [8, 8, 8, 8, 9, 10],[12, 15, 18, 19, 21, 23], [5, 5, 6, 7, 7, 8],[10, 13, 15, 18, 20, 22]]
discount = np.reshape([0, 10, 12, 15, 18, 20], [6,1])


def revenue(params):
    products_sold = []
    Pi = []
    for i in range(len(sold)):
        Pi.append( mean(sold[i]) / N[i] )

    for i in range(n):
        factor = 0
        # for j in range(m):
        #     factor += f[j]*F[i][j]
        # products_sold.append(factor * N[i] * params[i])
        products_sold.append((1+factor) * Pi[i]*N[i] * (params[i]/100 * f[i]) +1 )

    R=0
    Rp.clear()
    for i in range(n):
        tmp = p[i] * (1-params[i]/100) * products_sold[i]
        Rp.append(tmp)
        R += tmp

    return -R   #-ve sign as the optimizer module has only minimize function


def transpose(l1):
    l2 =[[row[i] for row in l1] for i in range(len(l1[0]))]
    return l2


def data_input(request):
    # if request.method =='POST':

        # print(request.user.socialaccount_set.all()[0].extra_data)


        ######################## Input ############################

        for i in range(len(sold.copy())):
            for j in range(len(sold[0].copy())-1):
                key = "t" + str(i+1) + str(j+1)
                sold[i][j+1] = int(request.POST[key])

        # month = request.POST["month"]

        for i in range(len(p.copy())):
            key = "p" + str(i+1)
            p[i] = int(request.POST[key])

        for i in range(len(N.copy())):
            key = "n" + str(i+1)
            N[i] = int(request.POST[key])

        print("Sold", sold)

        ####################### Calculating the slopes using linear regression ##############################3
        cnt = len(sold)
        beta = 0
        beta_vs_temp = []
        for count in range(cnt):
            reg = LinearRegression().fit(discount, np.array(sold[count], dtype = float).reshape([6,1]))
            beta_vs_temp.append(reg.coef_)
            beta += reg.coef_
        beta_avg = beta/7
        print(beta_vs_temp)
        print(beta_avg)

        for i in range(len(f.copy())):
            f[i] = beta_vs_temp[i][0][0]

        print('Factors: ', f)


        ################### Optimizing the function to get discounts ##########################
          

        initial_guess = [10, 10, 10, 10 ,10] #discount to be applied
        # result = optimize.minimize(revenue, initial_guess)
        bnds = ((0, 40),(0, 20),(5, 40),(0, 20),(10, 50))
        result = optimize.minimize(revenue, initial_guess, method='TNC', bounds=bnds)
        if result.success:
            fitted_params = result.x
            print(fitted_params)
            print(-revenue(fitted_params))
        else:
            raise ValueError(result.message)



        #################### Data Generation ########################

        dis = [0, 10, 12, 15, 18, 20,30,40,50,60,70,80]

        p_vs_d = []
        for d in dis:
            d_arr = [d]*n
            R = -revenue(d_arr)
            p_vs_d.append(list(Rp))
            # print(R, Rp)
            # print(a)


        p_vs_d = transpose(p_vs_d.copy())
        print(p_vs_d)


        ############################### Plotting time ###############################

        sns.set_style("darkgrid")

        figure, axes = plt.subplots(1, 5, sharex=True, figsize=(16,4))
        figure.suptitle('Discount Strategy for products')

        for i in range(len(p_vs_d)):
            y_label = "P"+str(i+1)+" Revenue"
            data = {y_label: p_vs_d[i], 'Discount': dis}
            df = pd.DataFrame(data)
            sns.lineplot(ax=axes[i], y=y_label, x='Discount', data=df)

        # plt.show()


        chart = get_graph()
        plt.savefig("me308/static/resources/images/result.png", format="png")
        
        print('Suggested Discounts: ', fitted_params)

        with open('me308/static/resources/discount.txt', 'wb') as handle:
            pickle.dump(fitted_params, handle, protocol=pickle.HIGHEST_PROTOCOL)

        return redirect('data-result')


def data_result(request):

    with open('me308/static/resources/discount.txt', 'rb') as f:
        dis = pickle.load(f)

    for i in range(len(dis)):
        dis[i] = round(dis[i],2)

    print('dis: ', dis)

    return render(request, 'data-result.html', {'dis':dis})

