from django.shortcuts import render,redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.db.models.query_utils import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserModel
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.conf import settings
from .forms import GenericModelMainForm, GenericModelForeignForm, CustomUserCreationForm, PasswordResetForm, PasswordResetConfirmForm, LoginForm

from .forms import PeopleModelForm, VaccineModelForm, EstablishmentModelForm, HealthcareModelForm
from .models import GenericModelForeign, GenericModelMain, PeopleModel, EstablishmentModel, RoleModel, TracingModel, HealthcareModel
from django.views.decorators.http import require_http_methods
from django.core import serializers
import json
from .utils import make_http_response

@login_required
def dashboard(request):
    context = {
        'active_page':'Dashboard',
    }
    return render(request, 'mainapp/dashboard.html', context)

def read_objects(request):
    context = {
        'active_page':'Read Objects',
        'form': GenericModelMainForm(),
        'all_data': GenericModelMain.objects.all(),
    }
    return render(request, 'mainapp/read_objects.html', context)

def create_object(request):
    if request.method == 'POST':
        form = GenericModelMainForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Action succeeded.')
            return redirect('mainapp:read_objects')
        else:
            messages.error(request, 'Action failed, validate your inputs.')

def update_object(request, pk):
    if request.method == 'POST':
        instance = get_object_or_404(GenericModelMain,pk=pk)
        form = GenericModelMainForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Action succeeded.')
            return redirect(request.path_info)
        else:
            messages.error(request, 'Action failed, validate your inputs.')
    
    instance = get_object_or_404(GenericModelMain,pk=pk)
    
    context = {
        'active_page':'Read Objects',
        'form': GenericModelMainForm(instance=instance),
        'instance': instance
        
    }
    return render(request, 'mainapp/update_object.html', context)

def delete_object(request, pk):
    instance = get_object_or_404(GenericModelMain,pk=pk)
    instance.delete()
    messages.success(request, 'Action succeeded.')
    return redirect('mainapp:read_objects')



def login_user(request):
    if request.user.is_authenticated:
        more_info = get_object_or_404(RoleModel, user_info=request.user)
        if more_info.role == 'citizen':
            return redirect('mainapp:personal_info_people')
        elif more_info.role == 'healthcare':
            return redirect('mainapp:alert_healthcare')
        elif more_info.role == 'establishment':
            return redirect('mainapp:trace_establishment')
    context = {}
    if request.method == 'POST':
        form = LoginForm()
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            more_info = get_object_or_404(RoleModel, user_info=user)
            print(more_info.role)
            if more_info.role == 'citizen':
                print(1)
                return redirect('mainapp:personal_info_people')
            elif more_info.role == 'healthcare':
                print(2)
                return redirect('mainapp:alert_healthcare')
            elif more_info.role == 'establishment':
                print(3)
                return redirect('mainapp:trace_establishment')
        else:
            context['form'] = form
            messages.error(request, 'Invalid login credentials.')
            return redirect('mainapp:login')
    else:
        context['form'] = LoginForm()
        context['reset_form'] = PasswordResetForm()
        context['signup_form'] = CustomUserCreationForm()
    return render(request, 'mainapp/accounts/login.html', context)


def user_create(request):
    context = {}
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        username_error = None
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully.')
            return HttpResponseRedirect(reverse('mainapp:login'))
        else:
            username_error = form.errors.as_data()['username']
            if username_error:
                messages.error(request, 'Action failed, username has been taken.')
                return redirect('mainapp:login')
            context['form'] = form
            messages.error(request, 'Action failed, validate your inputs.')
    else:
        context['form'] = CustomUserCreationForm()
    return redirect('mainapp:login')

def user_password_reset(request):
    context = {}
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user_list = User.objects.filter(Q(email=email))
            if user_list.exists():
                user = user_list[0]
                message_context = {'protocol': 'http',
                                   'domain': request.get_host(),
                                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                   'token': default_token_generator.make_token(user),
                                   'receiver_name': f"{user.first_name} {user.last_name}"}
                message_plain = render_to_string("mainapp/email/password_reset.txt", message_context)
                message_html = render_to_string("mainapp/email/password_reset.html", message_context)
                send_mail('Password Reset', message_plain, settings.DEFAULT_FROM_EMAIL, [email], html_message = message_html)
                messages.success(request, 'If your email address is registered, you will receive a reset link and ensure to check your spam folder.')
                return redirect('mainapp:login')
            else:
                messages.success(request, 'If your email address is registered, you will receive a reset link and ensure to check your spam folder.')
                return redirect('mainapp:login')
        else:
            context['form'] = form
            messages.error(request, 'Action failed, validate your inputs.')
            return redirect('mainapp:login')

def user_password_reset_confirm(request, uid, token):
    context = {'uid': uid,
               'token': token}
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            decoded_uid = urlsafe_base64_decode(uid)
            user = get_object_or_404(User, pk=decoded_uid)
            new_password = form.cleaned_data['password2']
            user.set_password(new_password)
            user.save()
            messages.success(request, 'You may now log in to your account.')
            return redirect('mainapp:login')
        else:
            context['form'] = form
            messages.error(request, 'Action failed, validate your inputs.')
    else:
        context['form'] = PasswordResetConfirmForm
    decoded_uid = urlsafe_base64_decode(uid)
    user = get_object_or_404(User, pk=decoded_uid)
    context['email'] = user.email
    return render(request, 'mainapp/accounts/password_reset_confirm.html', context)

model_mapping = {}
modelform_mapping = {}

@require_http_methods(["GET"])
def ajax_read_objects(request, model_string):
    if request.is_ajax:
        pk = request.GET.get('pk')
        model = model_mapping[model_string]
        if pk:
            data = get_object_or_404(model, pk=pk)
        else:
            data = model.objects.all()
        response_data = {
            'status': 'success',
            'message': 'Action succeeded.',
            'data': [data]
        }
        response = HttpResponse(
            json.dumps(response_data),
            content_type="application/json",
            status_code =200
        )
        return response
 

@require_http_methods(["POST"])
def ajax_create_object(request, model_string):
    if request.is_ajax:
        model_form = modelform_mapping[model_string]
        form = model_form(json.loads(request.body))
        if form.is_valid():
            form.save()
            response_data = {
                'status': 'success',
                'message': 'Action succeeded.',
                'data':[]
            }
            response = HttpResponse(
                json.dumps(response_data),
                content_type="application/json",
            )
            response.status_code = 200
            return response
        else:
            response_data = {
                'status': 'error',
                'message': 'Action failed, validate your inputs.',
                'data':[]
            }
            response = HttpResponse(
                json.dumps(response_data),
                content_type="application/json",
            )
            response.status_code = 400
            return response
        
@require_http_methods(["GET"])
def ajax_read_objects(request, model_string):
    if request.is_ajax:
        pk = request.GET.get('pk')
        model = model_mapping[model_string]
        if pk:
            data = get_object_or_404(model, pk=pk)
        else:
            data = model.objects.all()
        response_data = {
            'status': 'success',
            'message': 'Action succeeded.',
            'data': [data]
        }
        response = HttpResponse(
            json.dumps(response_data),
            content_type="application/json",
            status_code =200
        )
        return response
 


def create_people(request):
    if request.method == 'POST':
        form1 = CustomUserCreationForm(request.POST,prefix="form1")
        form2 = PeopleModelForm(request.POST, request.FILES, prefix="form2")
        if form1.is_valid():
            form1.save()
            data = get_object_or_404(User, email=form1.cleaned_data['email'])
            
            form2.instance.user_info = data
            if form2.is_valid():
                form2.save()
                role = RoleModel(user_info=data, role='citizen')
                role.save()
                messages.success(request, 'Account successfully created.')
                return redirect("mainapp:login")
            else:
                instance = get_object_or_404(User, email=form1.cleaned_data['email'])
                instance.delete()
                print(form2.errors)
                messages.error(request, 'Action failed, validate your inputs.')
        else:
            print(form1.errors)
            messages.error(request, 'Action failed, validate your inputs.')
    context = {
        'form1': CustomUserCreationForm(prefix="form1"),
        'form2': PeopleModelForm(prefix="form2")
    }
    return render(request, 'mainapp/people/register.html', context)

@login_required
def personal_info_people(request):
    instance = get_object_or_404(PeopleModel, user_info=request.user)
    context = {
        'active_page':'Personal',
        'form': PeopleModelForm(instance=instance),
        'instance':instance
    }
    return render(request, 'mainapp/people/personal_info.html', context)

@login_required
def vaccination_info_people(request):
    if request.method == 'POST':
        instance = get_object_or_404(GenericModelMain,pk=pk)
        form = GenericModelMainForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Action succeeded.')
            return redirect(request.path_info)
        else:
            messages.error(request, 'Action failed, validate your inputs.')
    
    instance = get_object_or_404(GenericModelMain,pk=pk)
    
    context = {
        'active_page':'Vaccination Info',
        'form': GenericModelMainForm(instance=instance),
        'instance': instance
        
    }
    return render(request, 'mainapp/update_object.html', context)
    return render(request, 'mainapp/people/personal_info.html', context)





def create_establishment(request):
    if request.method == 'POST':
        form1 = CustomUserCreationForm(request.POST,prefix="form1")
        form2 = EstablishmentModelForm(request.POST, prefix="form2")
        if form1.is_valid():
            form1.save()
            data = get_object_or_404(User, email=form1.cleaned_data['email'])
            
            form2.instance.user_info = data
            form2.instance.role = 'establishment'
            if form2.is_valid():
                form2.save()
                role = RoleModel(user_info=data, role='establishment')
                role.save()
                messages.success(request, 'Account successfully created.')
                return redirect("mainapp:login")
            else:
                data.delete()
                print(form2.errors)
                messages.error(request, 'Action failed, validate your inputs.')
        else:
            print(form1.errors)
            messages.error(request, 'Action failed, validate your inputs.')
    context = {
        'form1': CustomUserCreationForm(prefix="form1"),
        'form2': EstablishmentModelForm(prefix="form2")
    }
    return render(request, 'mainapp/establishment/register.html', context)

@login_required
def trace_establishment(request):
    if request.method == 'POST':
        id = request.POST['user_info']
        user_info = get_object_or_404(UserModel,id=id)
        establishment = get_object_or_404(EstablishmentModel, user_info=request.user)

        tracing = TracingModel(user_info=user_info.id,establishment=establishment.id)
        tracing.save()
        messages.success(request, 'Successfully added to contact tracing record.')
        return redirect(request.path_info)
    context = {
        'active_page':'Tracing',
        'establishment_name': get_object_or_404(EstablishmentModel, user_info=request.user)
    }
    id = request.GET.get('id')
    
    if id:
        try:
            id = int(id)
        except:
            id = 0
        try:
            person = get_object_or_404(UserModel, id=id)
            details = get_object_or_404(PeopleModel, user_info = person)
            context['person'] = person
            context['details'] = details
        except Exception as err:
            print(err)
    
    
    return render(request, 'mainapp/establishment/tracing.html', context)

@login_required
def view_trace_establishment(request):
    all = TracingModel.objects.all()
    all_data = []
    for item in all:
        user = get_object_or_404(UserModel,pk=item.user_info)
        date = item.date
        all_data.append(
            {
                'name':f"{user.last_name}, {user.first_name}",
                'email': user.email,
                'date':date
            }
        )
    context = {
        'active_page':'History',
        'all_data': all_data,
        'establishment_name': get_object_or_404(EstablishmentModel, user_info=request.user)
    }
    return render(request, 'mainapp/establishment/view_tracing.html', context)







def create_healthcare(request):
    if request.method == 'POST':
        form1 = CustomUserCreationForm(request.POST,prefix="form1")
        form2 = HealthcareModelForm(request.POST, prefix="form2")
        if form1.is_valid():
            form1.save()
            data = get_object_or_404(User, email=form1.cleaned_data['email'])
            
            form2.instance.user_info = data
            form2.instance.role = 'healthcare'
            if form2.is_valid():
                form2.save()
                role = RoleModel(user_info=data, role='healthcare')
                role.save()
                messages.success(request, 'Account successfully created.')
                return redirect("mainapp:login")
            else:
                data.delete()
                print(form2.errors)
                messages.error(request, 'Action failed, validate your inputs.')
        else:
            print(form1.errors)
            messages.error(request, 'Action failed, validate your inputs.')
    context = {
        'form1': CustomUserCreationForm(prefix="form1"),
        'form2': EstablishmentModelForm(prefix="form2")
    }
    return render(request, 'mainapp/healthcare/register.html', context)

@login_required
def alert_healthcare(request):
    if request.method == 'POST':
        id = request.POST['user_info']
        user_info = get_object_or_404(UserModel,id=id)
        establishment = get_object_or_404(EstablishmentModel, user_info=request.user)

        
        messages.success(request, 'Successfully added to contact tracing record.')
        return redirect(request.path_info)
    context = {
        'active_page':'Tracing',
        'establishment_name': get_object_or_404(HealthcareModel, user_info=request.user)
    }
    
    return render(request, 'mainapp/healthcare/alert.html', context)









# BAD REQUEST
def handle400(request, exception):
    return render(request, 'mainapp/400.html', status=400)

# PERMISSION DENIED
def handle403(request, exception):
    return render(request, 'mainapp/403.html', status=403)

# PAGE NOT FOUND
def handle404(request, exception):
    return render(request, 'mainapp/404.html', status=404)

# SERVER ERROR
def handle500(request):
    return render(request, 'mainapp/500.html', status=500)
