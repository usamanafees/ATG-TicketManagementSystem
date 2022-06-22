# Description
This is ticketing managements/reporting system like (os tickets) It has
the features to add different organization and their independent
reporting and managements.



This file contains instructions regarding to the setup of ATG-Extra on new Machine.

1. Create Virtual Environment
2. pip install -r requirements.txt
3. django-admin createproject ATG_itrak
4. django-admin startapp itrak
5. Make changes to the settings.py file
6. Before run migration add custom model for User and add below line in settings.py
AUTH_USER_MODEL = 'itrak.User' #Change the Built-In User Model#
7. Run Migration
8. Add First Organization directly to associate with First User
