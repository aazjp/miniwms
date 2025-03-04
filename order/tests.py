from django.test import TestCase,Client
from customer.models import Customer
from . import models

from django.urls import reverse
import logging
import sqlite3

# Create your tests here.
class test_order_add(TestCase):
    logging.info("启动测试order")
    def setUp(self) -> None:
        self.c=Client()
        self.cus1=Customer.objects.create(name='测试客户1',phone='1380000000')
        self.cus2=Customer.objects.create(name='测试客户2',phone='1380000000')
        self.cus3=Customer.objects.create(name='测试客户3',phone='1380000000')


    def test_order_add(self):

        logging.info("测试order_add")

        self.c.get(reverse('order:order_add'))
        logging.info("尝试post  order_add")
        self.c.post(reverse('order:order_add'),data={
            'code':'1234567890',
            'date':'2022-01-01',
            'customer_id':self.cus1.id,
            'customer_name':self.cus1.name,
            'status':'1',
        })
        print("数据库中order的数量为:",models.Order.objects.all().count())

        cus_id_get=models.Order.objects.get(customer_id=self.cus1.id)
        print(cus_id_get.customer_name)
        self.assertEqual(cus_id_get.customer_name,self.cus1.name)
        cus_name_get=models.Order.objects.get(customer_name=self.cus1.name)
        self.assertEqual(cus_name_get.customer_name,self.cus1.name)