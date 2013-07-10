"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test.simple import DjangoTestSuiteRunner
class NoTestDbDatabaseTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self, **kwargs):
        pass
    def teardown_databases(self, old_config, **kwargs):
        pass
    

