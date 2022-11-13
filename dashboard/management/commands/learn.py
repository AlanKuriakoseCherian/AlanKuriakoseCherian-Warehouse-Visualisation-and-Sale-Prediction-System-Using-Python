C
import pandas as pd
from django.core.management import BaseCommand
from django.db.models import Sum, F, Value
from django.db.models.functions import Concat
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

from dashboard.models import Order
import pickle


class Command(BaseCommand):

    def get_data(self):
        """
        Returns the value, {
            product_id1: [
                ('month1' ,'year', 'total'), ('month2' ,'year1', 'total'), , ('month3' ,'year1', 'total'),
            ],
            product_id2: [
                ('month1' ,'year', 'total'), ('month2' ,'year1', 'total'), , ('month3' ,'year1', 'total'),
            ],
            ...
            ...
            ...
            product_idn: [
                ('month1' ,'year', 'total'), ('month2' ,'year1', 'total'), , ('month3' ,'year1', 'total'),
            ],
        ]
        """
        qs = Order.objects.all().values('name', 'created_at__month', 'created_at__year').annotate(
                total=Sum('order_quantity') * F('name__mrp')).values(
                'name', 'created_at__month', 'created_at__year', 'total'
            )
        out = defaultdict(list)
        print("Fetching DATA FROM DATA SOURCE............................")
        for row in qs:
            out[row['name']].append([row['created_at__month'], row['created_at__year'], row['total']])
        print("DATA LOADED...................................!!")
        for key, val in out.items():
            print(f"PRODuCT : {key}\t\t DATA: {len(val)}")
        return out

    def handle(self, *args, **kwargs):

        # df = pd.read_excel(r'Book1.xlsx')
        dataset = self.get_data()
        print(dataset)
        for product_id, data in dataset.items():
            df = pd.DataFrame(data)

            # Segregating
            x = df.iloc[:, :-1].values
            y = df.iloc[:, -1].values

            # dividing into train and test
            print("Learning for  Product ID : ", product_id)
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, train_size=0.7, random_state=0)


            regressor = LinearRegression()
            regressor.fit(x_train, y_train)

            # prediction
            y_pred = regressor.predict(x_test)
            print("Prediction Accuracy Score :\t ", r2_score(y_test, y_pred), "[GOOD]")
            with open(f'trained_data/SaleModel__{product_id}.pkl', 'wb') as f:        # earlier 'salemodel.pkl'
                pickle.dump(regressor, f)
