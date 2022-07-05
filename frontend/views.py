from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from backend.models import Country, Category, Project, Media
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
# Create your views here.


@csrf_exempt
def login(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        w_user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if not w_user is None :
            auth.login(request, w_user)

            return redirect('/')
        else:
            template = loader.get_template('frontend/login.html')
            form.errors['error'] = "error"
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))

    if request.method == "GET":
        form = AuthenticationForm
        template = loader.get_template('frontend/login.html')
        context = {'form': form}
        return HttpResponse(template.render(context, request))


@csrf_exempt
def logout(request):
    auth.logout(request)
    return redirect('/')


@csrf_exempt
@login_required(login_url='/login')
def index(request):
    template = loader.get_template('frontend/top.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def setting(request):
    template = loader.get_template('frontend/setting.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def region(request):
    template = loader.get_template('frontend/region.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def country(request):
    country_id = request.GET.get('id', 'JP')
    w_country = Country.objects.get(country_id=country_id)
    template = loader.get_template('frontend/country.html')
    context = {
        'country_id': country_id,
        'country_name': w_country.country_name if w_country else "",
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def category(request):
    template = loader.get_template('frontend/category.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def detail(request):
    project_idx = request.GET.get('id', 0)
    template = loader.get_template('frontend/detail.html')
    context = {
        'project_idx': project_idx
    }
    return HttpResponse(template.render(context, request))


