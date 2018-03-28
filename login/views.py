from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse,HttpResponseRedirect
#from . import models
#from . import forms
from .models import User
from .models import ConfirmString
from .forms import UserForm
from .forms import RegisterForm
from .forms import PasswordForm,ForgetpassForm,ResetpassForm
import hashlib
import datetime
from django.conf import settings


# Create your views here.

def index(request):
	return render(request,'login/index.html')

def login(request):
	if request.session.get('is_login',None):
		return redirect('/index/')

	if request.method == 'POST':
		login_form = UserForm(request.POST)
		
		message = "所有字段都必须填写！"
		if login_form.is_valid():
			#data = login_form.cleaned_data
			#return HttpResponse(data)
			#die()
			username = login_form.cleaned_data['username']
			password = login_form.cleaned_data['password']
			
			try:
				user = User.objects.get(name=username)
				
				if not user.has_confirmed:
					message = "该用户还未通过邮箱确认！"
					return render(request,'login/login.html',locals())

				if user.password == hash_code(password):
					request.session['is_login'] = True
					request.session['user_id'] = user.id
					request.session['user_name'] = user.name
					return redirect('/index/')
				else:
					message = "密码不正确！"

				if login_form.captcha.errors:
					message = "验证码错误！"
			except:
				message = "用户名不存在！"


		return render(request,'login/login.html',locals())
	
	login_form = UserForm()		
	return render(request,'login/login.html',locals())


def register(request):
	if request.session.get('is_login',None):
		return redirect("/index/")

	if request.method == "POST":
		register_form = RegisterForm(request.POST)
		message = "请检查填写的内容!"
		if register_form.is_valid():
			username = register_form.cleaned_data['username']
			password1 = register_form.cleaned_data['password1']
			password2 = register_form.cleaned_data['password2']
			email = register_form.cleaned_data['email']
			sex = register_form.cleaned_data['sex']
			if password1 != password2:
				message = "两次密码不一致！"
				return render(request,'login/register.html',locals())
			else:
				same_name_user = User.objects.filter(name=username)
				if same_name_user:
					message = "用户已经存在，请重新选择用户名！"
					return render(request,'login/register.html',locals())
				same_email_user = User.objects.filter(email=email)
				if same_email_user:
					message = "该邮箱地址已经注册，请使用别的邮箱！"
					return render(request,'login/register.html',locals())

				#一切情况OK的状态下，保存信息到数据库
				new_user = User.objects.create()
				new_user.name = username
				new_user.password = hash_code(password1)
				new_user.email = email
				new_user.sex = sex
				new_user.save()

				code = make_confirm_string(new_user)
				send_mail(email,code)
				message = "请前往注册邮箱，进行邮箱确认!"
				return render(request,'login/confirm.html',locals())

	register_form = RegisterForm(request.POST)

	return render(request,'login/register.html',locals())

def logout(request):
	if not request.session.get('is_login',None):
		return redirect("/index/")
	request.session.flush()
	# 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
	return redirect("/index/")

def password(request):
	
	username = request.session.get('user_name')
	if request.method == "POST":
		password_form = PasswordForm(request.POST)
		message = '请检查填写的内容'
		if password_form.is_valid():
			#username = password_form.cleaned_data['username']
			password1 = password_form.cleaned_data['password1']
			password2 = password_form.cleaned_data['password2']
			if password1 != password2:
				message = "两次密码不一致！"
				return render(request,'login/password.html',locals())
			try:
				user = User.objects.filter(name=username)
				pwd= hash_code(password1)
				user.update(password=pwd)
				message = "密码修改成功！稍后返回首页！"
				return render(request,"login/confirm.html",locals())
			except:
				message = "用户名不存在！"

	password_form = PasswordForm(request.POST)	
	return render(request,'login/password.html',locals())



def user_confirm(request):
	code = request.GET.get('code',None)
	message = ''
	try:
		confirm = ConfirmString.objects.get(code=code)
	except:
		message = "无效的确认请求！"
		return render(request,'login/confirm.html',locals())

	c_time = confirm.c_time
	now = datetime.datetime.now()
	if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
		confirm.user.delete()
		message = "你的邮件已过期，请重新注册！"
		return render(request,'login/confirm.html',locals())
	else:
		confirm.user.has_confirmed = True
		confirm.user.save()
		confirm.delete()
		message = "感谢确认，请使用账号登录！"
		return render(request,'login/confirm.html',locals())


def forgetpass(request):
	if request.method == "POST":
		pw_reset_form = ForgetpassForm(request.POST)
		message = "请检查填写的内容!！！！！！！！！"
		if pw_reset_form.is_valid():
			
			email = pw_reset_form.cleaned_data['email']

			users = User.objects.get(email=email)
			if users:
				username = users.name
				now = datetime.datetime.now().strftime("%Y-%m_%d %H:%M:%S")
				code = hash_code(username,now)

				pw_reset_send_mail(email,username,code)
				message = "请前往邮箱进行重置密码"
				return render(request,'login/confirm.html',locals())
			else:
			 	message = "用户邮箱不存在，请重新输入"
			 	return render(request,'login/forgetpass.html',locals())

	pw_reset_form = ForgetpassForm(request.POST)
	return render(request,'login/forgetpass.html',locals())


def resetpass(request):
	code = request.GET.get('code',None)
	message = ''
	# if not code:
	# 	message = "无效的确认请求！"
	# 	return render(request,'login/resetconfirm.html',locals())

	# c_time = confirm.c_time
	# now = datetime.datetime.now()
	# if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
	# 	confirm.user.delete()
	# 	message = "你的邮件已过期，请重新注册！"
	# 	return render(request,'login/resetconfirm.html',locals())

	# else:
	if request.method == "POST":
		password_reset_form = ResetpassForm(request.POST)
		message = '请检查填写的内容'
		if password_reset_form.is_valid():
			username = password_reset_form.cleaned_data['username']
			password1 = password_reset_form.cleaned_data['password1']
			password2 = password_reset_form.cleaned_data['password2']
			if password1 != password2:
				message = "两次密码不一致！"
				return render(request,'login/resetpass.html',locals())
			try:
				user = User.objects.filter(name=username)
				pwd= hash_code(password1)
				user.update(password=pwd)
				message = "密码修改成功！稍后返回首页！"
				return render(request,"login/resetconfirm.html",locals())
			except:
				message = "用户名不存在！"

	password_reset_form = ResetpassForm(request.POST)	
	return render(request,'login/resetpass.html',locals())

def reset_password_confirm(request):
	return render(request,'login/reset_password_confirm.html',locals())
	

def hash_code(s,salt='mysite'):
	h = hashlib.sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def make_confirm_string(user):
	now = datetime.datetime.now().strftime("%Y-%m_%d %H:%M:%S")
	code = hash_code(user.name,now)
	ConfirmString.objects.create(code=code,user=user)
	return code


def send_mail(email,code):
	from django.core.mail import EmailMultiAlternatives
	subject = '来自www.liujiangblog.com的注册确认邮件'
	text_content = '感谢注册www.liujiangblog.com，这里是刘江的博客和教程站点！'
	html_content = '''
					<p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>www.liujiangblog.com</a>，这里是刘江的博客和教程站点，专注于Python和Django技术的分享！</p>
    				<p>请点击站点链接完成注册确认！</p><p>此链接有效期为{}天！</p>
    				'''.format('127.0.0.1:8000', code, settings.CONFIRM_DAYS)
	msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
	msg.attach_alternative(html_content, "text/html")
	msg.send()


def pw_reset_send_mail(email,username,code):
	from django.core.mail import EmailMultiAlternatives
	subject = '来自www.liujiangblog.com的密码重置邮件'
	text_content = '你收到这封邮件是因为你请求重置你在网站的用户账户密码。请访问该页面并选择一个新密码：'
	html_content = '''
					<p><a href="http://{}/resetpass/?code={}" target=blank>www.liujiangblog.com</a>，你的用户名，如果已忘记的话：{} </p>
					<p>感谢使用我们的站点！</p><p>此链接有效期为{}天！</p>
					'''.format('127.0.0.1:8000', code, username, settings.CONFIRM_DAYS)
	msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
	msg.attach_alternative(html_content, "text/html")
	msg.send()

