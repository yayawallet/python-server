# yaya-python-server
This is a server for yaya python example dashboard to demonstrate the usage of yayawallet-python-sdk package. The server is implemented using Django framework.

# Environment
You have to set the following environment variables for the project to run successfully.
```
YAYA_API_URL=https://sandbox.yayawallet.com/api/en
YAYA_API_PATH=/api/en
POSTGRES_DB={YOUR_DATABASE_NAME}
POSTGRES_USER={YOUR_DATABASE_USER}
POSTGRES_PASSWORD={YOUR_DATABASE_PASSWORD}
DJANGO_SUPERUSER_USERNAME={SUPERUSER_USERNAME}
DJANGO_SUPERUSER_EMAIL={SUPERUSER_EMAIL}
DJANGO_SUPERUSER_PASSWORD={SUPERUSER_PASSWORD}
{user1_api_key}_YAYA_API_SECRET={user1_api_secret}
{user2_api_key}_YAYA_API_SECRET={user2_api_secret}
...more user secret keys, if available
```
NOTE: The user api keys should not have a hyphen in the name, so you should replace all hyphens with underscore. For example, 'key-test_b4ra65rr-s4q0' should be 'key_test_b4ra65rr_s4q0'.

# How to run it?
The project is dockerized, so you can simply run it by running the following command in the terminal:
```
docker-compose up
```

# Configuration
Once you run the project, go to the admin module and login using the credentials you set for superadmin on environment variables. Then go to groups, select Admin Group and add the following permissions to that group:
```
auth | user | Can add user
auth | user | Can change user
auth | user | Can delete user
auth | user | Can view user
dashboard | user profile | Can add user profile
dashboard | user profile | Can change user profile
dashboard | user profile | Can delete user profile
dashboard | user profile | Can view user profile
auth | group | Can view group
auth | permission | Can view permission
```


# How to test
To test the functionality, you can use postman desktop application. Ypu can find the available services in the following file:
```
python_server/urls.py
```