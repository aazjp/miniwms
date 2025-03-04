from django.test import TestCase,Client


# Create your tests here.

class style_add(TestCase):
    def setUp(self) -> None:
        self.c=Client()
        
        return super().setUp()