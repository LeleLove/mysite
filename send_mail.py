import os
from django.core.mail import send_mail,EmailMultiAlternatives

#通过os设置环境变量
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

if __name__ == '__main__':
	# send_mail(
	# 	'来自myiste.django.com的测试邮件',#邮件主题
	# 	'欢迎访问mysite.django.com,这里是Django测试网站!',#邮件具体内容
	#  	'15201542092m@sina.cn',#邮件发送方，与settings中的一致
	#  	'956433007@qq.com',#邮件接收方地址列表
	# )

	subject = "来自myiste.django.com的测试邮件"
	from_email = "15201542092m@sina.cn"
	to = "956433007@qq.com"
	text_content = "欢迎访问mysite.django.com,这里是Django测试网站!"
	html_content = "<p>欢迎访问<a href='http://www.baidu.com' target=blank>mysite.django.com</a>,这里是Django测试网站!</p>"
	msg = EmailMultiAlternatives(subject,text_content,from_email,[to])
	msg.attach_alternative(html_content,'text/html')
	msg.send()