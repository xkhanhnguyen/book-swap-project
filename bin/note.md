source .venv/bin/activate

chmod +x ./bin/file_name

<!-- checklist of settings -->
python3 manage.py check --deploy


<!-- to get new app(folder) install -->
python3 manage.py startapp app_name

Note:
## Admin User has no profile
in case login to admin site and got the error (User has no profile) ![Alt text](image.png)
[stackoverflow](https://stackoverflow.com/questions/52385596/relatedobjectdoesnotexist-at-admin-login-user-has-no-profile)

-Enter a python terminal in your virtual environment

```python manage.py shell```

-Run this, will fix your issue without blowing out the database
```
from django.contrib.auth.models import User
from users.models import Profile
user = User.objects.get(username='enter_admin_user_here')
profile = Profile(user=user)
profile.save()
```

This will add a user profile for the admin user.

This command will copy the django-ckeditor static and media resources into the directory given by the STATIC_ROOT.

`python manage.py collectstatic`