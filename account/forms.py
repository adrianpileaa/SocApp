from django import forms
from .models import Account, Post
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):
	email = forms.EmailField()
	
	class Meta:
		model = Account
		fields = ('email', 'username', 'password1', 'password2')

	
	def clean_email(self):
		email = self.cleaned_data.get('email').lower()
		try:
			account = Account.objects.get(email = email)
		except Exception as e:
			return email
		raise forms.ValidationError(f'Email {email} already exists!')
		
	def clean_username(self):
		username = self.cleaned_data.get('username')
		try:
			account = Account.objects.get(username = username)
		except Exception as e:
			return username
		raise forms.ValidationError(f'Username {username} already exists')
	

class AuthenticationForm(forms.ModelForm):
	password = forms.CharField(max_length = 30, widget = forms.PasswordInput)
	
	class Meta:
		model = Account
		fields = ('email', 'password')
	
	def clean(self):
		email = self.cleaned_data.get('email')
		password = self.cleaned_data.get('password')
		user = authenticate(email = email, password = password)
		if not user:		
			raise forms.ValidationError('Login Invalid')
		return self.cleaned_data

class EditProfileForm(forms.ModelForm):
	class Meta:
		model = Account
		fields = ('email', 'username', 'profile_picture', 'bio')

	def clean_email(self):
		email = self.cleaned_data['email']
		try:
			account = Account.objects.exclude(pk = self.instance.pk).get(email = email)
		except Account.DoesNotExist:
			return email
		raise forms.ValidationError('Invalid Email')

	def clean_username(self):
		username = self.cleaned_data['username']
		try:
			account = Account.objects.exclude(pk = self.instance.pk).get(username = username)
		except Account.DoesNotExist:
			return username
		raise forms.ValidationError('Username Invalid')
	


	def save(self, commit = True):
		account = super(EditProfileForm, self).save(commit = False)
		account.email = self.cleaned_data['email']
		account.username = self.cleaned_data['username']
		account.profile_picture = self.cleaned_data['profile_picture']
		account.bio = self.cleaned_data['bio']
		if commit:
			account.save()
		return account

class NewPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ('writer', 'description', 'picture',)