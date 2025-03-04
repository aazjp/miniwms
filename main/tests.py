from django.test import TestCase,Client
from django.urls import reverse
from django.test import RequestFactory
from django.template import Context, Template
from django.shortcuts import render,HttpResponse,redirect
import os
# Create your tests here.
class PathTestCase(TestCase):
    def setUp(self) :
        self.c=Client()
  
    def test_path(self):
        
        path = ['main:login_view','main:logined_base','main:logout_view','main:register_view']     
        for i in path:
            self.c.get(reverse (i))