from math import radians, sin, cos, asin, sqrt
import matplotlib.pyplot as plt
import seaborn as sns


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Compute distance between two pairs of coordinates (lon1, lat1, lon2, lat2)
    See - (https://en.wikipedia.org/wiki/Haversine_formula)
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * 6371 * asin(sqrt(a))


def return_significative_coef(model):
    """
    Returns p_value, lower and upper bound coefficients
    from a statsmodels object.
    """
    # Extract p_values
    p_values = model.pvalues.reset_index()
    p_values.columns = ['variable', 'p_value']

    # Extract coef_int
    coef = model.params.reset_index()
    coef.columns = ['variable', 'coef']
    return p_values.merge(coef,
                          on='variable')\
                   .query("p_value<0.05").sort_values(by='coef',
                                                      ascending=False)


def plot_kde_plot(df, variable, dimension):
    """
    Plot a side by side kdeplot for `variable`, split
    by `dimension`.
    """
    g = sns.FacetGrid(df,
                      hue=dimension,
                      col=dimension)
    g.map(sns.kdeplot, variable)

def get_financials(df):
    """
    Returns a df with 'revenue', 'costs', 'it_costs', '
    """
    df['months_of_sales']=((df['date_last_sale']-df['date_first_sale']).dt.days+1)*(12/365)
    df['monthly_sales']=(df['sales']/(df['months_of_sales']))*0.1+80
    df['month_integer']=df['months_of_sales'].apply(lambda x: int(x)+1)

    df['monthly_costs']=((df['share_of_one_stars']*df['n_orders']*100)+df['share_of_two_stars']*df['n_orders']*50+df['share_of_three_stars']*df['n_orders']*40)/(df['months_of_sales'])
    #calculating IT costs contribution     0.5MM=k*sqrt(total_orders)  for each seller: ITCost=k*sqrt(n_order)
    df['monthly_costs_IT']=0
    #total cost
    totalcost=500000
    #sum square orders of Olist
    total_orders=(df['n_orders']).sum()
    #calculating k
    k=totalcost/((total_orders)**0.5)
    #calculating each seller cost
    df['monthly_costs_IT']=((df['n_orders']/total_orders)*totalcost)/(df['months_of_sales'])
    df['monthly_costs_total']=df['monthly_costs']+df['monthly_costs_IT']

    df['monthly_profit']=df['monthly_sales']-df['monthly_costs_total']

    return df
