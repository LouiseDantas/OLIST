import os
import pandas as pd
import numpy as np
from olist.utils import haversine_distance
from olist.data import Olist


class Order:
    '''
    DataFrames containing all orders as index,
    and various properties of these orders as columns
    '''

    def __init__(self):
        # Assign an attribute ".data" to all new instances of Order
        self.data = Olist().get_data()

    def get_wait_time(self, is_delivered=True):
        """
        Returns a DataFrame with:
        [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        and filters out non-delivered orders unless specified
        """
        # Hint: Within this instance method, you have access to the instance of the class Order in the variable self, as well as all its attributes
        # $CHALLENGIFY_BEGIN
        # make sure to create a copy rather than a "view"
        orders = self.data['orders'].copy()

        # filter delivered orders
        if is_delivered:
            orders = orders.query("order_status=='delivered'").copy()

        # handle datetime
        orders.loc[:, 'order_delivered_customer_date'] = \
            pd.to_datetime(orders['order_delivered_customer_date'])
        orders.loc[:, 'order_estimated_delivery_date'] = \
            pd.to_datetime(orders['order_estimated_delivery_date'])
        orders.loc[:, 'order_purchase_timestamp'] = \
            pd.to_datetime(orders['order_purchase_timestamp'])

        # compute delay vs expected
        orders.loc[:, 'delay_vs_expected'] = \
            (orders['order_delivered_customer_date'] -
             orders['order_estimated_delivery_date']) / np.timedelta64(24, 'h')

        def handle_delay(x):
            # We only want to keep delay where wait_time is longer than expected (not the other way around)
            # This is what drives customer dissatisfaction!
            if x > 0:
                return x
            else:
                return 0

        orders.loc[:, 'delay_vs_expected'] = \
            orders['delay_vs_expected'].apply(handle_delay)

        # compute wait time
        orders.loc[:, 'wait_time'] = \
            (orders['order_delivered_customer_date'] -
             orders['order_purchase_timestamp']) / np.timedelta64(24, 'h')

        # compute expected wait time
        orders.loc[:, 'expected_wait_time'] = \
            (orders['order_estimated_delivery_date'] -
             orders['order_purchase_timestamp']) / np.timedelta64(24, 'h')

        return orders[['order_id', 'wait_time', 'expected_wait_time',
                       'delay_vs_expected', 'order_status']]
        # $CHALLENGIFY_END

    def get_review_score(self):
        """
        Returns a DataFrame with:
        order_id, dim_is_five_star, dim_is_one_star, review_score
        """
        reviews = self.data['order_reviews'].copy()
        #identifying 5 stars
        reviews['dim_is_five_star']=np.zeros(len(reviews['review_score']))
        reviews.loc[reviews['review_score']==5,['dim_is_five_star']]=1
        #identifying 4 stars
        reviews['dim_is_four_star']=np.zeros(len(reviews['review_score']))
        reviews.loc[reviews['review_score']==4,['dim_is_four_star']]=1
        #identifying 3 stars
        reviews['dim_is_three_star']=np.zeros(len(reviews['review_score']))
        reviews.loc[reviews['review_score']==3,['dim_is_three_star']]=1
        #identifying 2 stars
        reviews['dim_is_two_star']=np.zeros(len(reviews['review_score']))
        reviews.loc[reviews['review_score']==2,['dim_is_two_star']]=1
        #identifying 1 star
        reviews['dim_is_one_star']=np.zeros(len(reviews['review_score']))
        reviews.loc[reviews['review_score']==1,['dim_is_one_star']]=1

        return reviews[['order_id','dim_is_five_star','dim_is_one_star','dim_is_two_star','dim_is_three_star','dim_is_four_star','review_score']]

    def get_number_products(self):
        """
        Returns a DataFrame with:
        order_id, number_of_products
        """
        oproducts = self.data['order_items'].copy()
        #grouping by the order_id and counting how many products there is in an unique order_id
        product_count=oproducts.groupby('order_id').count()
        #reseting index so index is not the order_id anymore
        product_count.reset_index(level=0, inplace=True)
        product_count=product_count[['order_id','product_id']]
        product_count=product_count.rename(columns={"product_id": "number_of_products"})
        return product_count

    def get_number_sellers(self):
        """
        Returns a DataFrame with:
        order_id, number_of_sellers
        """
        order_details=self.data['order_items']
        order_seller=order_details.groupby('order_id')[['seller_id']].nunique()
        order_seller.reset_index(level=0, inplace=True)
        order_seller=order_seller.rename(columns={"seller_id": "number_of_sellers"})
        return order_seller


    def get_price_and_freight(self):
        """
        Returns a DataFrame with:
        order_id, price, freight_value
        """
        order_costs=self.data['order_items']
        order_costs=order_costs.groupby('order_id')[['price','freight_value']].sum()
        order_costs.reset_index(level=0, inplace=True)
        return order_costs

    # Optional
    def get_distance_seller_customer(self):
        """
        Returns a DataFrame with order_id
        and distance_seller_customer
        """
        pass  # YOUR CODE HERE

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        """
        Returns a clean DataFrame (without NaN), with the all following columns:
        ['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected',
        'order_status', 'dim_is_five_star', 'dim_is_one_star', 'review_score',
        'number_of_products', 'number_of_sellers', 'price', 'freight_value',
        'distance_seller_customer']
        """
        df_wait_time=self.get_wait_time()

        df_review=self.get_review_score()

        df_number_products=self.get_number_products()

        df_number_sellers=self.get_number_sellers()

        df_price_freight=self.get_price_and_freight()


        df_training_data=df_wait_time.merge(df_review,how='inner',on='order_id')
        df_training_data=df_training_data.merge(df_number_products,how='inner',on='order_id')
        df_training_data=df_training_data.merge(df_number_sellers,how='inner',on='order_id')
        df_training_data=df_training_data.merge(df_price_freight,how='inner',on='order_id')

        return df_training_data.dropna(axis=0)
