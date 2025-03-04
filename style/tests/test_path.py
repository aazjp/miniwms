from ast import arguments
from django.test import TestCase, Client
from django.urls import reverse
from django.test import RequestFactory
from django.template import Context, Template
from django.shortcuts import render, HttpResponse, redirect
import os
from .. import models
from main.models import USERINFO as User


class PathTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create(username="admin", password="admin")
        self.color_1 = models.Color.objects.create(color="红色", code="001")
        self.color_2 = models.Color.objects.create(color="黑色", code="002")
        self.size = models.Size.objects.create(size="M", code="01")
        self.designer_1 = models.Designer.objects.create(name="张三", code="01")
        self.designer_2 = models.Designer.objects.create(name="李四", code="02")
        self.type = models.Type.objects.create(name="裤子", code="10001")

        self.style_1 = models.Style.objects.create(
            name="短裤",
            code="100010100101",
            designer=self.designer_1,
            color=self.color_1,
            size=self.size,
            type=self.type,
            price_cost=100,
            price_retail=100,
            price_wholesale=100,
            remark="备注"
        )
        self.style_2 = models.Style.objects.create(
            name="长裤裤",
            code="100020200101",
            designer=self.designer_1,
            color=self.color_1,
            size=self.size,
            type=self.type,
            price_cost=100,
            price_retail=100,
            price_wholesale=100,
            remark="备注"
        )

    def test_style_manage(self):
        response = self.c.get(reverse('style:style_manage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'style/style/style_manage.html')
        self.assertTrue(response.context['style_info'])

    def test_color_add(self):
        # get
        response = self.c.get(reverse('style:color_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'style/color/color_add.html')
        #  post
        self.c.post(reverse('style:color_add'),
                    {'color': '红色',
                     'code': '001'
                     },)
        self.assertEqual(models.Color.objects.get(color=self.color_1.color), self.color_1)

    def test_style_add(self):
        # get
        response = self.c.get(reverse('style:style_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'style/style/style_add.html')
        self.assertTrue(response.context['data']['color_info'])
        self.assertTrue(response.context['data']['size_info'])
        self.assertTrue(response.context['data']['designer_info'])
        self.assertTrue(response.context['data']['type_info'])
        #  post
        self.c.post(reverse('style:style_add'),
                    {'name': '短裤',
                     'designer': self.designer_2.code,
                     'color': self.color_1.code,
                     'size': self.size.code,
                     'type': self.type.code,
                     'price_cost': 100,
                     'price_retail': 100,
                     'price_wholesale': 100,
                     'remark': '备注'
                     })
        self.assertEqual(models.Style.objects.get(
            designer__name=self.designer_2.name).designer.name, self.designer_2.name)

    def test_style_update(self):

        response = self.c.get(reverse('style:style_update', args=[self.style_1.code]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'style/style/style_update.html')
        self.assertTrue(response.context['data']['color_info'])
        self.assertTrue(response.context['data']['style_info'])
        #  post
        self.c.post(reverse('style:style_update', args=[self.style_1.code]),
                    {'name': '短裤',
                     'price_cost': 100,
                     'price_retail': 100,
                     'price_wholesale': 100,
                     'remark': '备注'
                     })
                     
        self.assertEqual(models.Style.objects.get(code=self.style_1.code), self.style_1)
       
    def test_style_delete(self):
        pre_del=models.Style.objects.all().count()
        response = self.c.get(reverse('style:style_delete', args=[self.style_1.code]))
        after_del=models.Style.objects.all().count()
        self.assertEqual(after_del,pre_del-1)
        # self.assertEqual(response.status_code, 200)

    
    def test_color_add(self):
        # get
        response = self.c.get(reverse('style:color_add'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'style/color/color_add.html')
        #  post
        self.c.post(reverse('style:color_add'),
                    {'color': '绿色',
                     'code': '003'
                     },)
                     
        self.assertEqual(models.Color.objects.get(color='绿色').color,'绿色' )
        
    def test_color_update(self):
        response = self.c.get(reverse('style:color_update', args=[self.color_1.code]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'style/color/color_update.html')
        
        self.c.post(reverse('style:color_update', args=[self.color_1.code]),
                    {'color': '黑色',
                     'code': '001'
                     },)
                     
        self.assertEqual(models.Color.objects.get(code=self.color_1.code).color, '黑色')
        
    def test_color_delete(self):
        pre_del=models.Color.objects.all().count()
        response = self.c.get(reverse('style:color_delete', args=[self.color_1.code]))
        after_del=models.Color.objects.all().count()
        self.assertEqual(after_del,pre_del-1)
        # self.assertEqual(response.status_code, 200)

    
    

        
