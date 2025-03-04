from django.test import TestCase,Client
from django.urls import reverse
from django.test import RequestFactory
from django.template import Context, Template
from django.shortcuts import render,HttpResponse,redirect
import os

class PathTestCase(TestCase):
    def setUp(self) :
        self.c=Client()
        self.request=RequestFactory()
  
    def test_path(self):
        
        path = ['inventory:inventory','inventory:inventory_add','inventory:inventory_out','inventory:inventory_record','inventory:record_filter',]     
        for i in path:
            self.c.get(reverse (i)) 
                         
       