from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse)
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import (
	RegistrationForm, 
	AuthenticationForm, 
	EditProfileForm,
	NewPostForm)
from .models import (
	Account, 
	Post, 
	Like, 
	Comment, 
	ChatRoomName,
	Message
	)
import json
import random

@login_required
def home(request):
	context = {}
	user = request.user
	all_users = Account.objects.all()
	whatevers=[]
	
	for each in all_users:
		if user in each.following.all():
			whatevers.append(Post.objects.filter(writer_id=each.id))
	last_list = []
	for l in whatevers:
		for element in l:
			dictionaryy = {
			'post' : '',
			'likes' : '',
			'is_liked' : '',
			'comments' : '',
			}
			post = Post.objects.get(pk = element.id)
			like, created = Like.objects.get_or_create(post = post)
			likes_number = like.likes.all().count()
			comments = Comment.objects.filter(post = post)
			is_liked = False
			if user in like.likes.all():
				is_liked = True
			dictionaryy['post'] = element
			dictionaryy['likes'] = likes_number
			dictionaryy['is_liked'] = is_liked
			dictionaryy['comments'] = comments
			last_list.append(dictionaryy)
	context['all_dicts'] = last_list	
	list_len = len(all_users)
	all_sugestions = []
	n = random.sample(range(1,list_len),4)
	for i in n:
		if i != request.user.id:
			all_sugestions.append(Account.objects.get(id = i))
	self_account = Account.objects.get(username = request.user.username)
	context['self_account'] = self_account
	context['all_sugestions'] = all_sugestions
	return render(request, 'account/home.html', context)

def register_view(request, *args, **kwargs):
	user = request.user
	if user.is_authenticated:
		return HttpResponse(f"You already have an account as user {user}")
	context= {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = request.POST['email']
			raw_password = request.POST['password2']
			user = authenticate(email = email, password = raw_password)
			if user:
				login(request, user)
				destination = get_next_destination(request)
				if destination:
					return destination
				return redirect('account:home')
		context['registration_form'] = form
	else:
		form = RegistrationForm()
		context['registraton_form'] = form
	return render(request, 'account/register.html', context)


def login_view(request, *args, **kwargs):
	user = request.user 
	if user.is_authenticated:
		return redirect("account:home")
	context = {}
	if request.POST:
		form = AuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			raw_password = request.POST['password']
			account = authenticate(email = email, password = raw_password)
			if account:
				login(request, account)
				destination = get_next_destination(request)
				if destination:
					return destination
				return redirect("account:home")
	else:
		form = AuthenticationForm()
	return render(request, 'account/login.html', {'login_form' : form})


def logout_view(request):
	logout(request)
	return redirect('account:login')


def get_next_destination(request):
	redirect = None
	if request.GET:
		if request.GET.get('next'):
			redirect = str(request.GET.get('next'))
	return redirect

def account_view(request, username):
	context = {}
	account = Account.objects.get(username = username)
	if account:
		context['username'] = account.username
		context['profile_picture'] = account.profile_picture.url
		context['bio'] = account.bio
		context['author'] = account
		is_self = True 
		user = request.user
		if user != account:
			is_self = False
		if not user:
			is_self = False
		context['is_self'] = is_self
		if is_self:
			postes = Post.objects.filter(writer = user)
			context['postes'] = postes
		else:
			postes = Post.objects.filter(writer = account)
			context['postes'] = postes
		all_rooms = ChatRoomName.objects.all()
		new_list = []
		for i in all_rooms:
			new_list.append(i.name)

		current_name=f"{account.username}_{request.user.username}" 
		second_name=f"{request.user.username}_{account.username}"
		if current_name in new_list:
			room_q = ChatRoomName.objects.get(name = current_name)
		elif second_name in new_list:
			room_q = ChatRoomName.objects.get(name = second_name)
		else:
			room_q = ChatRoomName(name = second_name)
			room_q.save()
		context['room_name'] = room_q
		context['special'] = request.user.username
		following = False
		if request.user in account.following.all():
			following = True 
		context['following'] = following

	return render(request, 'account/account.html', context)


def edit_view(request, username, **kwargs):
	context = {}

	user_id = request.user.pk
	username = request.user.username
	if not request.user:
		return HttpResponse("You must be logged in")
	account = Account.objects.get(pk = user_id)
	if account.pk != request.user.pk:
		return HttpResponse("You can't edit someone else's profile")
	if request.POST:
		form = EditProfileForm(request.POST, request.FILES, instance = request.user)
		if form.is_valid():
			form.save()
			return redirect('account:view', username=request.user.username)
		else:
			form = EditProfileForm(request.POST, request.FILES, instance = request.user,
				initial = {
					'id' : account.id,
					'email' : account.email,
					'username' : account.username,
					'profile_picture' : account.profile_picture.url,
					'bio' : account.bio
				}
			)
			context['form'] = form
	else: 
		form = EditProfileForm(
				initial = {
					'id' : account.id,
					'email' : account.email,
					'username' : account.username,
					'profile_picture' : account.profile_picture.url,
					'bio' : account.bio
				}
			) 
		context['form']  = form
	return render(request, 'account/edit.html', context)

def search_view(request, *args, **kwargs):
	context = {}
	if request.method == 'GET':
		search_query = request.GET.get('q')
		if len(search_query) > 0:
			search_results = Account.objects.filter(email__icontains=search_query).filter(username__icontains=search_query).distinct()
			accounts = []
			for account in search_results:
				accounts.append(account)
			context['accounts'] = accounts
	return render(request, 'account/account_search.html', context)

def followToggle(request, author):
	authorObj = Account.objects.get(username = author)
	currentUserObj = Account.objects.get(username = request.user.username)
	following = authorObj.following.all()

	if author != currentUserObj.username:
		if currentUserObj in following:
			authorObj.following.remove(currentUserObj.id)
		else:
			authorObj.following.add(currentUserObj.id)
	return redirect('account:view', username = authorObj.username)


def post_view(request, pk, writer):
	context = {}
	post = Post.objects.get(pk = pk)
	like, created = Like.objects.get_or_create(post = post)
	likes_number = like.likes.all().count()
	is_liked = False
	if request.user in like.likes.all():
		is_liked = True
	comments = Comment.objects.filter(post = post)
	context['comments'] = comments
	context['likes_number']= likes_number
	context['is_liked'] = is_liked
	context['post'] = post
	context['myself'] = request.user.username
	return render(request, 'account/post_view.html', context)

def post_delete(request, pk, writer):
	post = Post.objects.get(pk = pk)
	if request.method == 'POST':
		post.delete()
		return redirect('account:view', username = request.user.username )
	return render(request, 'account/post_delete.html')


def new_post_view(request, writer):
	context = {}
	if request.method == "POST":
		form = NewPostForm(request.POST, request.FILES)
		if form.is_valid():
			description = form.cleaned_data.get('description')
			img = form.cleaned_data.get('picture')
			naming = Account.objects.get(username = request.user)

			obj = Post.objects.create(
				writer = naming,
				description = description,
				picture = img,
				)
			obj.save()
			return redirect('account:view', username=naming.username)
	else:
		form = NewPostForm()
	context['form'] = form
	context['myself'] = request.user.username
	return render(request, 'account/new_post.html', context)


def updateLikes(request):
	data = json.loads(request.body)
	postId = data['postId']
	action = data['action']
	user = request.user
	post = Post.objects.get(id = postId)
	like, created = Like.objects.get_or_create(post = post)
	if action == 'add':
		like.likes.add(user)
	elif action == 'remove':
		like.likes.remove(user)
	like.save()
	return JsonResponse('Like was added', safe = False)

def commentSend(request):
	data = json.loads(request.body)
	postId = data['postId']
	action = data['action']
	comment = data['comment']
	user = request.user
	post = Post.objects.get(id = postId)
	c = Comment.objects.create(post = post, user = user)
	if action == 'add-comment':
		c.c_itself=comment
	
	c.save()
	return JsonResponse('comment was added', safe = False)


def room(request, room_name, username):
	account  = Account.objects.get(username = username)
	userName = request.user.username
	messages = Message.objects.filter(room = room_name)
	return render(request, 'account/room.html', {
		'room_name' : room_name,
		'username' : userName,
		'account' : account,
		'messages' : messages
		})