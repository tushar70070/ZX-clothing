from email.message import EmailMessage
from tokenize import generate_tokens
from django.shortcuts import render,redirect,HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
# to Activate the user Accounts
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
#reset password Generator

from django.contrib.auth.tokens import PasswordResetTokenGenerator
# Getting token feom utils.py
from .utils import TokenGenerator,generate_token
#emails
from django.core.mail import send_mail,EmailMultiAlternatives
from django.core.mail import BadHeaderError,send_mail
from django.core import mail
from django.conf import settings
from django.core.mail import EmailMessage
# Threading
import threading 

class EmailThread(threading.Thread):
     
     def __init__(self,email_message):
         self.email_message=email_message
         threading.Thread.__init__(self)

     def run(self):
         self.email_message.send()    


class ActivateAccountView(View):

    def get(self,request,uidb64,token):

        try:

            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        except Exception as identifier:
            user = None
        if user is not None and generate_token.check_token(user,token)    :
            user.is_active=True   
            user.save()
            messages.info(request,'Account Activated Succsessfully')
            return redirect('login')
        
        return render(request,'auth/activatefail.html')


def signup(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 != pass2:

            messages.error(request,"Password Do Not Match ,Please Try Again")
            return redirect('signup')
        
        try:
            if User.objects.get(username = email):
                messages.warning(request,"Email Already Exists")
                return redirect('signup')
            
        except Exception as indentifier:
            pass

        user = User.objects.create_user(email,email,pass1)
        user.is_active=False
        user.save()
        current_site = get_current_site(request)
        domain = current_site.domain
        email_subject ="Aactivate Your Account"
        message = render_to_string('auth/activate.html',{
            'user':user,
            'domain':domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        }) 

        email_messgae = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        EmailThread(email_messgae).start()
        messages.success(request,'Activate Your Account Clicking link on your email')
        return redirect('login')



    return render(request,'auth/signup.html')


def login_user(request):
    if request.method == 'POST':

        loginusername=request.POST['email']
        loginpassword=request.POST['pass1']
        user=authenticate(request,username=loginusername,password=loginpassword)
       
        if user is not None:
            login(request,user)
            messages.info(request,"Successfully Logged In")
            return redirect('login')

        else:
            messages.error(request,"Invalid Credentials")
            return redirect('login')    

    return render(request,'auth/login.html')

def logouts(request):
    logout(request)
    messages.warning(request,"Logout Success")
    return render(request,'auth/login.html')


class RequestResetEmailView(View):

    def get(self,request):
        return render(request,'auth/request-reset-email.html')
    
    def post(self,request):
        email=request. POST['email']
        user = User.objects.filter(email=email)

        if user.exists():
            current_site = get_current_site(request)
            email_subject = '[Reset your Password]'
            domain = current_site.domain
            message = render_to_string('auth/reset-user-password.html',
                                       
                                       {
                                           'domain' :domain,
                                           'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                                           'token':PasswordResetTokenGenerator().make_token(user[0])
                                           
                                       })
            
            email_message = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
            EmailThread(email_message).start()

            messages.info(request,"We Have sent you an email with instructions on now to reset the password")
            return render(request,'auth/request-reset-email.html')
        
class SetNewPasswordView(View):
    def get(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token,

        }    
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)


            if  not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,'Password Reset link is Invalid')
                return render(request,'auth/request-reset-email.html')
        except DjangoUnicodeDecodeError as indentifier :
            pass

        return render(request,'auth/set-new-password.html',context)
    
    def post(self,request,uidb64,token):
        context = {
            'uidb64':uidb64,
            'token':token,
    
        }
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 != pass2:

            messages.error(request,"Password Do Not Match ,Please Try Again")
            return redirect('set-new-password.html',context)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)
            user.set_password(pass1)
            user.save()
            messages.success(request,'Password reset Success Please login with new passsword')
            return redirect('login')
        except DjangoUnicodeDecodeError as indetifire:
            messages.error(request,'Something went Wrong')
            return render(request,)

