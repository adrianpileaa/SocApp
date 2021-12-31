from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class AccountManager(BaseUserManager):
	def create_user(self,email, username ,password=None):
		if not email:
			raise ValidationError('A email should be provided')
		if not username:
			raise ValidationError('A username should be provided')
		user = self.model(
			email = self.normalize_email(email),
			username = username,
			)	
		user.set_password(password)
		user.save(using= self._db)
		return user
	
	def create_superuser(self, email, username, password):
		user = self.create_user(
			email=self.normalize_email(email),
			username = username,
			password = password,
			)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using = self._db)
		return user

def get_default_pic():
	return 'images/account-image.png'

def get_picture_path(self, pk):
	return f'images/{self.pk}/{"profile_image.png"}'



class Account(AbstractBaseUser):
	email = models.EmailField(max_length=255, unique = True, null = True, blank = False)
	username = models.CharField(max_length = 50, unique = True, null = True, blank=False)
	is_active = models.BooleanField(default = True)
	is_staff = models.BooleanField(default = False)
	is_admin = models.BooleanField(default = False)
	is_superuser = models.BooleanField(default = False)
	profile_picture = models.ImageField(default = get_default_pic, max_length=255, upload_to = get_picture_path)
	date_added = models.DateTimeField(auto_now_add=True, null = True)
	bio = models.CharField(max_length = 255, blank = True, null = True)
	following = models.ManyToManyField(
        "self", blank=True, related_name="followers", symmetrical=False
    )

	objects = AccountManager()

	USERNAME_FIELD =  'email'
	REQUIRED_FIELDS = ['username']

	def __str__(self):
		return self.username

	def has_perm(self, perm ,obj=None):
		return True

	def has_module_perms(self, app_label):
		return True

def get_posts_path(self, pk):
	return f'images/{self.writer.pk}/posts/{"post.png"}'

class Post(models.Model):
	writer = models.ForeignKey(Account, on_delete=models.SET_NULL, blank = True, null = True)
	description = models.CharField(max_length=255, blank = True, null = True)
	picture = models.ImageField(max_length = 255, upload_to = get_posts_path,blank = False, null = False)
	date_posted = models.DateTimeField(auto_now_add = True)

	def __str__(self):
		return self.description[0:20]


class Like(models.Model):
	post = models.OneToOneField(Post, on_delete=models.SET_NULL, null = True)
	likes = models.ManyToManyField(Account)
	def __str__(self):
		return str(self.post.id)

class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete = models.SET_NULL, null = True)
	user = models.ForeignKey(Account, on_delete = models.SET_NULL, null = True)
	c_itself = models.CharField(max_length = 200, blank=False)

	def __str__(self):
		return self.c_itself[0:20]

class ChatRoomName(models.Model):
	name = models.CharField(max_length = 255, blank=False, null = False)
	date_created = models.DateTimeField(auto_now_add = True)
	def __str__(self):
		return self.name

class Message(models.Model):
	username = models.CharField(max_length = 255)
	room = models.CharField(max_length = 255)
	content = models.TextField()
	data_added = models.DateTimeField(auto_now_add= True)

	class Meta:
		ordering = ('data_added', )


