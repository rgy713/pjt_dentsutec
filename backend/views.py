# -*- coding: utf-8 -*-

import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import auth
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import authenticate, update_session_auth_hash
from django.core.validators import validate_email
from django.db.models import Q
from os.path import splitext
from django import forms
from datetime import datetime
from django.utils import timezone
import calendar

from django.contrib.auth.models import User
from .models import Profile, Country, Category, Project, Media, Segment, Client, Company

# Create your views here.


@csrf_exempt
def login(request):
    if request.user.is_authenticated:
        return redirect('/admin/')

    if request.method == "POST":
        form = AdminAuthenticationForm(request, data=request.POST)
        w_user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
        if not w_user is None :
            auth.login(request, w_user)

            return redirect('/admin/')
        else:
            template = loader.get_template('frontend/login.html')
            form.errors['error'] = "error"
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))

    if request.method == "GET":
        form = AdminAuthenticationForm
        template = loader.get_template('frontend/login.html')
        context = {'form': form}
        return HttpResponse(template.render(context, request))


@csrf_exempt
def logout(request):
    auth.logout(request)
    return redirect('/admin/')


@csrf_exempt
@login_required(login_url='/login')
def index(request):
    w_user = request.user
    template = loader.get_template('backend/admin_home.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def user(request):
    w_user = request.user
    if w_user.is_superuser == 0:
        return project(request)

    template = loader.get_template('backend/admin_user.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def country(request):
    w_user = request.user
    template = loader.get_template('backend/admin_country.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def category(request):
    w_user = request.user
    template = loader.get_template('backend/admin_category.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def project(request):
    w_user = request.user
    template = loader.get_template('backend/admin_project.html')
    context = {
        'is_superuser': w_user.is_superuser,
        'user_profile': w_user.profile
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def client(request):
    w_user = request.user
    template = loader.get_template('backend/admin_client.html')
    context = {
        'is_superuser': w_user.is_superuser,
        'user_profile': w_user.profile
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def photo(request):
    w_user = request.user
    template = loader.get_template('backend/admin_photo.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def video(request):
    w_user = request.user
    template = loader.get_template('backend/admin_video.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def instagram(request):
    w_user = request.user
    template = loader.get_template('backend/admin_instagram.html')
    context = {
        'is_superuser': w_user.is_superuser
    }
    return HttpResponse(template.render(context, request))


@csrf_exempt
@login_required(login_url='/login')
def list_user(request):
    w_user = request.user
    if w_user.is_superuser == 0:
        return JsonResponse({})

    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        user_list = User.objects.filter(username__contains=s_key).order_by(orders)[start:start + length].values_list('id', 'username', 'is_superuser', 'profile__country__country_name', 'is_active')
        json_users = []
        all_users_count = User.objects.filter(username__contains=s_key).count()
        idx = 0
        for w_user in user_list:
            idx += 1
            number = start + idx
            json_user = {
                'number': number,
                'id': w_user[0],
                'username': w_user[1],
                'is_superuser': w_user[2],
                'profile__country__country_name': w_user[3],
                'status': w_user[4]
            }
            json_users.append(json_user)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_users_count,
            'recordsTotal': all_users_count,
            'data': json_users})
    else:
        user_list = User.objects.filter(is_active__exact=1)
        json_users = []
        for w_user in user_list:
            json_user = {
                'id': w_user.id,
                'username': w_user.username
            }
            json_users.append(json_user)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_users
        })


@csrf_exempt
@login_required(login_url='/login')
def create_user(request):
    w_user = request.user
    if w_user.is_superuser == 0:
        return JsonResponse({})

    response_data = {}

    w_user = request.user
    if w_user.is_superuser == 0:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_USER_PERMISSION'

        return JsonResponse(response_data)

    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    country = request.POST.get('country', None)
    name = request.POST.get('name', None)

    try:
        validate_email(email)
    except forms.ValidationError:
        response_data['type'] = 'error'
        response_data['content'] = 'ERR_INVALID_EMAIL'

        return JsonResponse(response_data)

    valid_count = User.objects.filter(username=username).count()
    if valid_count > 0:
        response_data['type'] = 'error'
        response_data['content'] = 'ERR_USERNAME_ALREADY_EXISTS'

        return JsonResponse(response_data)

    valid_count = User.objects.filter(email=email).count()
    if valid_count > 0:
        response_data['type'] = 'error'
        response_data['content'] = 'ERR_EMAIL_ALREADY_EXISTS'

        return JsonResponse(response_data)

    try:
        w_user = User.objects.create_user(username=username, email=email, password=password)

        w_user_profile = Profile.objects.get(user=w_user.id)
        if country is not None:
            w_user_profile.country_id = country

        if name is not None:
            w_user_profile.name = name

        w_user_profile.save()

    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_USER_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_user(request):
    w_user = request.user
    if w_user.is_superuser == 0:
        return JsonResponse({})

    response_data = {}

    w_user = request.user
    if w_user.is_superuser == 0:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_USER_PERMISSION'

        return JsonResponse(response_data)

    user_idx = request.POST.get('id', 0)
    username = request.POST.get('username', None)
    email = request.POST.get('email', None)
    country = request.POST.get('country', None)
    name = request.POST.get('name', None)
    status = request.POST.get('status', None)

    try:
        w_user = User.objects.get(id=user_idx)
        w_user_profile = Profile.objects.get(user=user_idx)
    except User.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_USER_UPDATE'

        return JsonResponse(response_data)

    if username is not None:
        valid_count = User.objects.exclude(id=user_idx).filter(username=username).count()
        if valid_count > 0:
            response_data['type'] = 'error'
            response_data['content'] = 'ERR_USERNAME_ALREADY_EXISTS'

            return JsonResponse(response_data)

        w_user.username = username

    if email is not None:
        try:
            validate_email(email)
        except forms.ValidationError:
            response_data['type'] = 'error'
            response_data['content'] = 'ERR_INVALID_EMAIL'

            return JsonResponse(response_data)

        valid_count = User.objects.exclude(id=user_idx).filter(email=email).count()
        if valid_count > 0:
            response_data['type'] = 'error'
            response_data['content'] = 'ERR_EMAIL_ALREADY_EXISTS'

            return JsonResponse(response_data)

        w_user.email = email

    if country is not None:
        w_user_profile.country_id = country

    if name is not None:
        w_user_profile.name = name

    if status is not None:
        w_user.is_active = status

    try:
        w_user.save()
        w_user_profile.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_USER_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_user(request):
    w_user = request.user
    if w_user.is_superuser == 0:
        return JsonResponse({})

    response_data = {}

    w_user = request.user
    if w_user.is_superuser == 0:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_USER_PERMISSION'

        return JsonResponse(response_data)

    if request.method == 'POST':
        user_idx = request.POST['id']

        json_user = {}

        try:
            w_user = Profile.objects.get(user=user_idx)
        except User.DoesNotExist:
            return JsonResponse(json_user)

        json_user = {
            'id': user_idx,
            'is_superuser': w_user.user.is_superuser,
            'username': w_user.user.username,
            'email': w_user.user.email,
            'password': w_user.user.password,
            'country': w_user.country.id if w_user.country else 0,
            'name': w_user.name
        }

        return JsonResponse(json_user)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_country(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        country_list = Country.objects.filter(country_name__contains=s_key).order_by(orders)[start:start + length]
        json_countries = []
        all_countries_count = Country.objects.filter(country_name__contains=s_key).count()
        idx = 0
        for w_country in country_list:
            idx += 1
            number = start + idx
            json_country = {
                'number': number,
                'id': w_country.id,
                'country_id': w_country.country_id,
                'country_name': w_country.country_name,
                'status': w_country.status
            }
            json_countries.append(json_country)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_countries_count,
            'recordsTotal': all_countries_count,
            'data': json_countries})
    else:
        country_list = Country.objects.filter(status__exact=1)
        json_countries = []
        for w_country in country_list:
            json_country = {
                'id': w_country.id,
                'country_id': w_country.country_id,
                'country_name': w_country.country_name
            }
            json_countries.append(json_country)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_countries
        })


@csrf_exempt
@login_required(login_url='/login')
def create_country(request):
    country_id = request.POST['country_id']
    country_name = request.POST['country_name']

    response_data = {}

    try:
        w_country = Country.objects.create(country_id=country_id, country_name=country_name)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_COUNTRY_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_country(request):
    country_idx = request.POST.get('id', 0)
    country_id = request.POST.get('country_id', None)
    country_name = request.POST.get('country_name', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_country = Country.objects.get(id=country_idx)
    except Country.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_COUNTRY_UPDATE'

        return JsonResponse(response_data)

    if country_id is not None:
        w_country.country_id = country_id

    if country_name is not None:
        w_country.country_name = country_name

    if status is not None:
        w_country.status = status

    try:
        w_country.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_COUNTRY_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_country(request):
    if request.method == 'POST':
        country_idx = request.POST['id']

        json_country = {}

        try:
            w_country = Country.objects.get(id=country_idx)
        except Country.DoesNotExist:
            return JsonResponse(json_country)

        json_country = {
            'id': w_country.id,
            'country_id': w_country.country_id,
            'country_name': w_country.country_name
        }

        return JsonResponse(json_country)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_category(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        category_list = Category.objects.filter(category_name__contains=s_key).order_by(orders)[start:start + length]
        json_categories = []
        all_categories_count = Category.objects.filter(category_name__contains=s_key).count()
        idx = 0
        for w_category in category_list:
            idx += 1
            number = start + idx
            json_category = {
                'number': number,
                'id': w_category.id,
                'category_id': w_category.category_id,
                'category_name': w_category.category_name,
                'status': w_category.status
            }
            json_categories.append(json_category)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_categories_count,
            'recordsTotal': all_categories_count,
            'data': json_categories})
    else:
        category_list = Category.objects.filter(status__exact=1)
        json_categories = []
        for w_category in category_list:
            json_category = {
                'id': w_category.id,
                'category_id': w_category.category_id,
                'category_name': w_category.category_name
            }
            json_categories.append(json_category)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_categories
        })


@csrf_exempt
@login_required(login_url='/login')
def create_category(request):
    category_id = request.POST['category_id']
    category_name = request.POST['category_name']

    response_data = {}

    try:
        w_category = Category.objects.create(category_id=category_id, category_name=category_name)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CATEGORY_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_category(request):
    category_idx = request.POST.get('id', 0)
    category_id = request.POST.get('category_id', None)
    category_name = request.POST.get('category_name', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_category = Category.objects.get(id=category_idx)
    except Category.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CATEGORY_UPDATE'

        return JsonResponse(response_data)

    if category_id is not None:
        w_category.category_id = category_id

    if category_name is not None:
        w_category.category_name = category_name

    if status is not None:
        w_category.status = status

    try:
        w_category.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CATEGORY_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_category(request):
    if request.method == 'POST':
        category_idx = request.POST['id']

        json_category = {}

        try:
            w_category = Category.objects.get(id=category_idx)
        except Category.DoesNotExist:
            return JsonResponse(json_category)

        json_category = {
            'id': w_category.id,
            'category_id': w_category.category_id,
            'category_name': w_category.category_name
        }

        return JsonResponse(json_category)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_segment(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        segment_list = Segment.objects.filter(segment_name__contains=s_key).order_by(orders)[start:start + length]
        json_segments = []
        all_segments_count = Segment.objects.filter(segment_name__contains=s_key).count()
        idx = 0
        for w_segment in segment_list:
            idx += 1
            number = start + idx
            json_segment = {
                'number': number,
                'id': w_segment.id,
                'segment_name': w_segment.segment_name,
                'status': w_segment.status
            }
            json_segments.append(json_segment)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_segments_count,
            'recordsTotal': all_segments_count,
            'data': json_segments})
    else:
        segment_list = Segment.objects.filter(status__exact=1)
        json_segments = []
        for w_segment in segment_list:
            json_segment = {
                'id': w_segment.id,
                'segment_name': w_segment.segment_name
            }
            json_segments.append(json_segment)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_segments
        })


@csrf_exempt
@login_required(login_url='/login')
def create_segment(request):
    segment_name = request.POST['segment_name']

    response_data = {}

    try:
        w_segment = Segment.objects.create(segment_name=segment_name)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_SEGMENT_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_segment(request):
    segment_idx = request.POST.get('id', 0)
    segment_name = request.POST.get('segment_name', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_segment = Segment.objects.get(id=segment_idx)
    except Segment.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_segment_UPDATE'

        return JsonResponse(response_data)

    if segment_name is not None:
        w_segment.segment_name = segment_name

    if status is not None:
        w_segment.status = status

    try:
        w_segment.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_SEGMENT_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_segment(request):
    if request.method == 'POST':
        segment_idx = request.POST['id']

        json_segment = {}

        try:
            w_segment = Segment.objects.get(id=segment_idx)
        except Segment.DoesNotExist:
            return JsonResponse(json_segment)

        json_segment = {
            'id': w_segment.id,
            'segment_name': w_segment.segment_name
        }

        return JsonResponse(json_segment)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_project(request):
    w_user = request.user
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)

        segment_key = request.POST.get('columns[5][search][value]', '')
        country_key = request.POST.get('columns[6][search][value]', '')

        project_list = Project.objects.filter(project_name__isnull=False)

        if len(s_key) > 0:
            project_list = project_list.filter(
                Q(project_name__icontains=s_key) | Q(client__client_name__icontains=s_key) | Q(client__company__company_name__icontains=s_key))

        if len(segment_key) > 0:
            project_list = project_list.filter(segment_id__exact=segment_key)

        if len(country_key) > 0:
            project_list = project_list.filter(register__profile__country_id__exact=country_key)

        all_project_count = project_list.count()
        project_list = project_list.order_by(orders)[start:start + length]

        json_projects = []
        idx = 0
        for w_project in project_list:
            idx += 1
            number = start + idx
            json_project = {
                'number': number,
                'id': w_project.id,
                'project_id': "P" + str(w_project.id),
                'project_name': w_project.project_name,
                'client__client_name': w_project.client.client_name if w_project.client is not None else '',
                'company_name': w_project.client.company.company_name if w_project.client is not None else '',
                'segment': w_project.segment.segment_name,
                'country': w_project.register.profile.country.country_name,
                'start_end_date': str(w_project.start_date) + '<br>' + str(w_project.end_date),
                'outline': w_project.outline,
                'result': w_project.result,
                'category__category_name': w_project.category.category_name,
                'status': w_project.status,
                'editable': w_user.is_superuser == 1 or w_user.profile.country.id == w_project.register.profile.country.id
            }
            json_projects.append(json_project)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_project_count,
            'recordsTotal': all_project_count,
            'data': json_projects})
    else:
        project_list = Project.objects.filter(status__exact=1)
        json_projects = []
        for w_project in project_list:
            json_project = {
                'id': w_project.id,
                'project_name': w_project.project_name
            }
            json_projects.append(json_project)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_projects
        })


@csrf_exempt
@login_required(login_url='/login')
def create_project_id(request):

    response_data = {}

    project_list = Project.objects.filter(project_name__isnull=True, status=0)

    if len(project_list) > 0:
        w_project = project_list[0]
    else:
        try:
            w_project = Project(
                register_id=request.user.id,
                start_date=datetime.now(),
                end_date=datetime.now(),
                client_id=Client.objects.first().id,
                category_id=Category.objects.first().id,
                segment_id=Segment.objects.first().id,
                status=0
            )
            w_project.save()

        except:
            response_data['type'] = 'E_FAIL'
            response_data['content'] = 'ERR_PROJECT_CREATE'

            return JsonResponse(response_data)

    response_data['type'] = 'S_OK'
    response_data['content'] = w_project.id

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def create_project(request):
    project_idx = request.POST.get('id', 0)
    project_name = request.POST['project_name']
    client = request.POST['client']
    start_date = request.POST['start_date']
    end_date = request.POST['end_date']
    outline = request.POST['outline']
    result = request.POST['result']
    w_category = request.POST['category']
    w_segment = request.POST['segment']

    response_data = {}

    try:
        if project_idx == 0:
            w_project = Project(
                status=1
            )

        else:
            w_project = Project.objects.get(id=project_idx)

        w_project.project_name = project_name
        w_project.register_id = request.user.id
        w_project.start_date = start_date
        w_project.end_date = end_date
        w_project.outline = outline
        w_project.result = result
        w_project.client_id = client
        w_project.category_id = w_category
        w_project.segment_id = w_segment
        w_project.status = 1
        w_project.save()

        upload_photo_files = request.FILES.getlist('file')

        if upload_photo_files:
            for i in range(0, len(upload_photo_files)):
                photo_file = upload_photo_files[i]
                regist_photo_file(photo_file, w_project.id, request.user.id)

        upload_video_urls = request.POST.get('create_videos', None)
        if upload_video_urls is not None:
            upload_video_urls = upload_video_urls.split(',')
            for video_url in upload_video_urls:
                regist_video_file(video_url, w_project.id, request.user.id)

    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_PROJECT_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'
    response_data['content'] = {
        'id': w_project.id,
        'number': w_project.id,
        'project_name': w_project.project_name,
        'country_id': w_project.register.profile.country.id,
        'country_name': w_project.register.profile.country.country_name,
        'client': w_project.client.id,
        'segment': w_project.segment.id,
        'company_name': w_project.client.company.company_name,
        'start_date': w_project.start_date,
        'end_date':w_project.end_date,
        'category': w_project.category.id,
        'outline': w_project.outline,
        'result': w_project.result
    }

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_project(request):
    project_idx = request.POST.get('id', 0)
    project_name = request.POST.get('project_name', None)
    segment = request.POST.get('segment', None)
    client = request.POST.get('client', None)
    start_date = request.POST.get('start_date', None)
    end_date = request.POST.get('end_date', None)
    outline = request.POST.get('outline', None)
    result = request.POST.get('result', None)
    w_category = request.POST.get('category', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_project = Project.objects.get(id=project_idx)
    except Project.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_PROJECT_UPDATE'

        return JsonResponse(response_data)

    if project_name is not None:
        w_project.project_name = project_name

    if client is not None:
        w_project.client_id = client

    if segment is not None:
        w_project.segment_id = segment

    if start_date is not None:
        w_project.start_date = start_date

    if end_date is not None:
        w_project.end_date = end_date

    if outline is not None:
        w_project.outline = outline

    if result is not None:
        w_project.result = result

    if w_category is not None:
        w_project.category_id = w_category

    if status is not None:
        w_project.status = status

    w_project.register_id = request.user.id

    try:
        w_project.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_PROJECT_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_project(request):
    if request.method == 'POST':
        project_idx = request.POST['id']

        json_project = {}

        try:
            w_project = Project.objects.get(id=project_idx)
        except Project.DoesNotExist:
            return JsonResponse(json_project)

        json_project = {
            'id': w_project.id,
            'project_name': w_project.project_name,
            'country_id': w_project.register.profile.country.id,
            'country_name': w_project.register.profile.country.country_name,
            'client': w_project.client.id if w_project.client is not None else '',
            'company_name': w_project.client.company.company_name if w_project.client is not None else '',
            'start_date': w_project.start_date,
            'end_date':w_project.end_date,
            'category': w_project.category.id,
            'segment': w_project.segment.id,
            'outline': w_project.outline,
            'result': w_project.result
        }

        return JsonResponse(json_project)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def delete_project(request):
    project_idx = request.POST.get('id', 0)

    response_data = {}

    try:
        w_project = Project.objects.get(id=project_idx)

        media_list = Media.objects.filter(project_id__exact=project_idx)
        for w_media in media_list:
            media_type = w_media.type
            if media_type == 0:
                delete_photo_file(w_media.id)
            elif media_type == 2:
                delete_video_file(w_media.id)

        w_project.delete()

    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_PROJECT_DELETE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def list_company(request):
    w_user = request.user
    if request.method == 'POST':

        company_list = Company.objects.filter(status__exact=1)

        json_companies = []
        for w_company in company_list:
            json_client = {
                'id': w_company.id,
                'company_name': w_company.company_name
            }
            json_companies.append(json_client)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_companies
        })
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def create_company(request):
    company_name = request.POST['company_name']

    response_data = {}

    try:
        w_company = Company.objects.create(
            company_name=company_name,
            status=1
        )
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_COMPANY_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_company(request):
    company_idx = request.POST.get('id', 0)
    company_name = request.POST.get('company_name', None)

    response_data = {}

    try:
        w_company = Company.objects.get(id=company_idx)
    except Company.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_COMPANY_UPDATE'

        return JsonResponse(response_data)

    if company_name is not None:
        w_company.company_name = company_name

    try:
        w_company.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_COMPANY_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_company(request):
    if request.method == 'POST':
        company_idx = request.POST['id']

        json_company = {}

        try:
            w_company = Company.objects.get(id=company_idx)
        except Client.DoesNotExist:
            return JsonResponse(json_company)

        json_company = {
            'id': w_company.id,
            'company_name': w_company.company_name,
            'note': w_company.note
        }

        return JsonResponse(json_company)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_client(request):
    w_user = request.user
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)

        country_key = request.POST.get('columns[3][search][value]', '')

        client_list = Client.objects.filter(client_name__isnull=False)

        if len(s_key) > 0:
            client_list = client_list.filter(Q(client_name__icontains=s_key) | Q(company__company_name__icontains=s_key))

        if len(country_key) > 0:
            client_list = client_list.filter(register__profile__country__id__exact=country_key)

        all_clients_count = client_list.count()

        client_list = client_list.order_by(orders)[start:start + length]

        json_clients = []
        idx = 0
        for w_client in client_list:
            idx += 1
            number = start + idx
            json_client = {
                'number': number,
                'id': w_client.id,
                'client_name': w_client.client_name,
                'company': w_client.company.company_name,
                'country_name': w_client.register.profile.country.country_name,
                'status': w_client.status,
                "editable": w_user.is_superuser == 1 or w_user.profile.country.id == w_client.register.profile.country.id
            }
            json_clients.append(json_client)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_clients_count,
            'recordsTotal': all_clients_count,
            'data': json_clients})
    else:
        client_list = Client.objects.filter(status__exact=1)
        json_clients = []
        for w_client in client_list:
            json_client = {
                'id': w_client.id,
                'client_name': w_client.client_name,
                'company': w_client.company.company_name
            }
            json_clients.append(json_client)

        return JsonResponse({
            'type': 'S_OK',
            'content': json_clients
        })


@csrf_exempt
@login_required(login_url='/login')
def create_client_id(request):
    response_data = {}

    client_list = Client.objects.filter(client_name__isnull=True, status=0)

    if len(client_list) > 0:
        w_client = client_list[0]
    else:
        try:
            w_client = Client(
                company_id=Company.objects.first().id,
                register_id=request.user.id,
                status=0
            )
            w_client.save()

        except:
            response_data['type'] = 'E_FAIL'
            response_data['content'] = 'ERR_CLIENT_CREATE'

            return JsonResponse(response_data)

    response_data['type'] = 'S_OK'
    response_data['content'] = w_client.id

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def create_client(request):
    client_idx = request.POST.get('id', 0)
    client_name = request.POST['client_name']
    company_idx = request.POST['company']
    company_name = request.POST['edit_company']
    w_note = request.POST['note']

    response_data = {}

    if len(company_idx) > 0:
        try:
            w_company = Company.objects.get(id=company_idx)
        except Company.DoesNotExist:
            response_data['type'] = 'E_FAIL'
            response_data['content'] = 'ERR_CLIENT_UPDATE'

            return JsonResponse(response_data)

        w_company.company_name = company_name.strip()
        w_company.save()

    else:
        try:
            w_company = Company.objects.create(
                company_name=company_name.strip(),
                status=1
            )
        except:
            response_data['type'] = 'E_FAIL'
            response_data['content'] = 'ERR_CLIENT_UPDATE'

            return JsonResponse(response_data)

        company_idx = w_company.id

    try:
        if client_idx == 0:
            w_client = Client(
                status=1
            )
        else:
            w_client = Client.objects.get(id=client_idx)

            w_client.client_name = client_name
            w_client.company_id = company_idx
            w_client.register_id = request.user.id
            w_client.note = w_note
            w_client.status = 1

            w_client.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CLIENT_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_client(request):
    client_idx = request.POST.get('id', 0)
    client_name = request.POST.get('client_name', None)
    company_idx = request.POST.get('company', None)
    company_name = request.POST.get('edit_company', None)
    status = request.POST.get('status', None)
    w_note = request.POST.get('note', None)

    response_data = {}

    try:
        w_client = Client.objects.get(id=client_idx)
    except Client.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CLIENT_UPDATE'

        return JsonResponse(response_data)

    if client_name is not None:
        w_client.client_name = client_name

    if company_idx is not None and company_name is not None:
        if len(company_idx) > 0:
            try:
                w_company = Company.objects.get(id=company_idx)
            except Client.DoesNotExist:
                response_data['type'] = 'E_FAIL'
                response_data['content'] = 'ERR_CLIENT_UPDATE'

                return JsonResponse(response_data)

            w_company.company_name = company_name.strip()
            w_company.save()

            w_client.company_id = w_company.id
        else:
            try:
                w_company = Company.objects.create(
                    company_name=company_name.strip(),
                    status=1
                )
            except:
                response_data['type'] = 'E_FAIL'
                response_data['content'] = 'ERR_CLIENT_UPDATE'

                return JsonResponse(response_data)

            w_client.company_id = w_company.id

    if status is not None:
        w_client.status = status

    if w_note is not None:
        w_client.note = w_note

    try:
        w_client.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CLIENT_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_client(request):
    if request.method == 'POST':
        client_idx = request.POST['id']

        json_client = {}

        try:
            w_client = Client.objects.get(id=client_idx)
        except Client.DoesNotExist:
            return JsonResponse(json_client)

        json_client = {
            'id': w_client.id,
            'client_name': w_client.client_name,
            'company': w_client.company.id,
            'country': w_client.register.profile.country.id,
            'country_name': w_client.register.profile.country.country_name,
            'note': w_client.note
        }

        return JsonResponse(json_client)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def delete_client(request):
    client_idx = request.POST.get('id', 0)

    response_data = {}

    try:
        w_client= Client.objects.get(id=client_idx)

        project_list = Project.objects.filter(client__id=client_idx)
        for w_project in project_list:
            w_project.client = None
            w_project.save()

        w_client.delete()

    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_CLIENT_DELETE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def list_photo(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        photo_list = Media.objects.filter(type__exact=0, title__contains=s_key).order_by(orders)[start:start + length]
        json_photos = []
        all_photos_count = Media.objects.filter(type__exact=0, title__contains=s_key).count()
        idx = 0
        for w_photo in photo_list:
            idx += 1
            number = start + idx
            json_photo = {
                'number': number,
                'id': w_photo.id,
                'media_id': w_photo.media_id,
                'url': w_photo.url,
                'thumb': w_photo.thumb,
                'title': w_photo.title,
                'project__project_name': w_photo.project.project_name,
                'project__client': w_photo.project.client.client_name,
                'regist_date': w_photo.regist_date,
                'register__username': w_photo.register.username,
                'status': w_photo.status
            }
            json_photos.append(json_photo)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_photos_count,
            'recordsTotal': all_photos_count,
            'data': json_photos})
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def create_photo(request):
    media_id = request.POST['media_id']
    title = request.POST['title']
    regist_date = request.POST['regist_date']
    register = request.POST['register']
    project = request.POST['project']
    upload_file = request.FILES['file']

    response_data = {}

    try:
        w_photo = Media.objects.create(
            type=0,
            media_id=media_id,
            title=title,
            regist_date=regist_date,
            register_id=register,
            project_id=project)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_CREATE'

        return JsonResponse(response_data)

    if upload_file:
        ext = splitext(upload_file.name)[1][1:].lower()
        file_name = str(w_photo.id) + '.' + ext
        w_photo.url = file_name
        w_photo.save()
        handle_uploaded_file(upload_file, file_name)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def regist_photo(request):
    response_data = {}

    project = request.POST['project']
    upload_files = request.FILES.getlist('file')
    register = request.user.id
    for i in range(0, len(upload_files)):
        upload_file = upload_files[i]
        response_data = regist_photo_file(upload_file, project, register)
        if response_data.get('type') == 'E_FAIL':
            return response_data

    return response_data


@csrf_exempt
def regist_photo_file(upload_file, project_idx, register_idx):
    regist_date = timezone.now()

    response_data = {}

    if upload_file:
        try:
            w_photo = Media.objects.create(
                type=0,
                regist_date=regist_date,
                register_id=register_idx,
                project_id=project_idx,
                status=1)
        except:
            response_data['type'] = 'E_FAIL'
            response_data['content'] = 'ERR_MEDIA_CREATE'

            return JsonResponse(response_data)

        response_data['type'] = 'S_OK'

        ext = splitext(upload_file.name)[1][1:].lower()
        file_name = str(w_photo.id) + '.' + ext
        w_photo.url = file_name
        w_photo.save()
        handle_uploaded_file(upload_file, file_name)

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def delete_photo(request):
    media_idx = request.POST.get('id', 0)

    return delete_photo_file(media_idx)


def delete_photo_file(photo_idx):
    response_data = {}

    try:
        w_photo = Media.objects.get(id=photo_idx)
        delete_file(w_photo.url)
        w_photo.delete()

    except Media.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_DELETE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_photo(request):
    media_idx = request.POST.get('id', 0)
    media_id = request.POST.get('media_id', None)
    title = request.POST.get('title', None)
    regist_date = request.POST.get('regist_date', None)
    register = request.POST.get('register', None)
    project = request.POST.get('project', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_photo = Media.objects.get(id=media_idx)
    except Media.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_UPDATE'

        return JsonResponse(response_data)

    if media_id is not None:
        w_photo.media_id = media_id

    if title is not None:
        w_photo.title = title

    if regist_date is not None:
        w_photo.regist_date = regist_date

    if register is not None:
        w_photo.register_id = register

    if project is not None:
        w_photo.project_id = project

    if status is not None:
        w_photo.status = status

    if request.FILES:
        upload_file = request.FILES['file']
        url = w_photo.url
        if url is not None and url != '':
            os.remove(os.path.join(settings.MEDIA_ROOT, 'images/' + url))

        ext = splitext(upload_file.name)[1][1:].lower()
        file_name = str(w_photo.id) + '.' + ext
        w_photo.url = file_name
        handle_uploaded_file(upload_file, file_name)

    try:
        w_photo.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_photo(request):
    if request.method == 'POST':
        media_idx = request.POST['id']

        json_photo = {}

        try:
            w_photo = Media.objects.get(id=media_idx)
        except Media.DoesNotExist:
            return JsonResponse(json_photo)

        json_photo = {
            'id': w_photo.id,
            'media_id': w_photo.media_id,
            'url': w_photo.url,
            'thumb': w_photo.thumb,
            'title': w_photo.title,
            'project': w_photo.project.id,
            'register': w_photo.register.id,
            'regist_date': w_photo.regist_date
        }

        return JsonResponse(json_photo)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_video(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        video_list = Media.objects.filter(type__exact=2, title__contains=s_key).order_by(orders)[start:start + length]
        json_videos = []
        all_videos_count = Media.objects.filter(type__exact=2, title__contains=s_key).count()
        idx = 0
        for w_video in video_list:
            idx += 1
            number = start + idx
            json_video = {
                'number': number,
                'id': w_video.id,
                'media_id': w_video.media_id,
                'url': w_video.url,
                'thumb': w_video.thumb,
                'title': w_video.title,
                'project__project_name': w_video.project.project_name,
                'project__client': w_video.project.client.client_name,
                'regist_date': w_video.regist_date,
                'register__username': w_video.register.username,
                'status': w_video.status
            }
            json_videos.append(json_video)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_videos_count,
            'recordsTotal': all_videos_count,
            'data': json_videos})
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def create_video(request):
    media_id = request.POST['media_id']
    title = request.POST['title']
    url = request.POST['url']
    thumb = request.POST['thumb']
    regist_date = request.POST['regist_date']
    register = request.POST['register']
    project = request.POST['project']

    response_data = {}

    try:
        w_video = Media.objects.create(
            type=2,
            media_id=media_id,
            title=title,
            url=url,
            thumb=thumb,
            regist_date=regist_date,
            register_id=register,
            project_id=project)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def regist_video(request):
    project = request.POST['project']
    url = request.POST['url']

    return regist_video_file(url, project, request.user.id)


def regist_video_file(video_url, project_idx, register_idx):
    response_data = {}

    if len(video_url) == 0:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_CREATE'

        return JsonResponse(response_data)

    thumb = video_url.replace("https://www.youtube.com/watch?v=", "")
    thumb = video_url.replace("https://youtu.be/", "")
    thumb = "http://i3.ytimg.com/vi/" + thumb + "/hqdefault.jpg"

    regist_date = timezone.now()

    try:
        w_video = Media.objects.create(
            type=2,
            url=video_url,
            thumb=thumb,
            regist_date=regist_date,
            register_id=register_idx,
            project_id=project_idx,
            status=1)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def delete_video(request):
    media_idx = request.POST.get('id', 0)

    return delete_video_file(media_idx)


def delete_video_file(video_idx):
    response_data = {}

    try:
        w_video = Media.objects.get(id=video_idx).delete()
    except Media.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_DELETE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_video(request):
    media_idx = request.POST.get('id', 0)
    media_id = request.POST.get('media_id', None)
    title = request.POST.get('title', None)
    url = request.POST.get('url', None)
    thumb = request.POST.get('thumb', None)
    regist_date = request.POST.get('regist_date', None)
    register = request.POST.get('register', None)
    project = request.POST.get('project', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_video = Media.objects.get(id=media_idx)
    except Media.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_UPDATE'

        return JsonResponse(response_data)

    if media_id is not None:
        w_video.media_id = media_id

    if title is not None:
        w_video.title = title

    if url is not None:
        w_video.url = url

    if thumb is not None:
        w_video.thumb = thumb

    if regist_date is not None:
        w_video.regist_date = regist_date

    if register is not None:
        w_video.register_id = register

    if project is not None:
        w_video.project_id = project

    if status is not None:
        w_video.status = status

    try:
        w_video.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_video(request):
    if request.method == 'POST':
        media_idx = request.POST['id']

        json_video = {}

        try:
            w_video = Media.objects.get(id=media_idx)
        except Media.DoesNotExist:
            return JsonResponse(json_video)

        json_video = {
            'id': w_video.id,
            'media_id': w_video.media_id,
            'url': w_video.url,
            'thumb': w_video.thumb,
            'title': w_video.title,
            'project': w_video.project.id,
            'register': w_video.register.id,
            'regist_date': w_video.regist_date
        }

        return JsonResponse(json_video)
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def list_instagram(request):
    if request.method == 'POST':
        draw = int(request.POST.get('draw', 1))
        s_key = request.POST.get('search[value]', '')
        start = int(request.POST.get('start', 0))
        length = int( request.POST.get('length', 10))
        orders = parse_order(request)
        instagram_list = Media.objects.filter(type__exact=1, title__contains=s_key).order_by(orders)[start:start + length]
        json_instagrams = []
        all_instagrams_count = Media.objects.filter(type__exact=1, title__contains=s_key).count()
        idx = 0
        for w_instagram in instagram_list:
            idx += 1
            number = start + idx
            json_instagram = {
                'number': number,
                'id': w_instagram.id,
                'media_id': w_instagram.media_id,
                'url': w_instagram.url,
                'hash_tag': w_instagram.hash_tag,
                'title': w_instagram.title,
                'project__project_name': w_instagram.project.project_name,
                'project__client': w_instagram.project.client,
                'regist_date': w_instagram.regist_date,
                'register__username': w_instagram.register.username,
                'status': w_instagram.status
            }
            json_instagrams.append(json_instagram)

        return JsonResponse({
            'draw': draw + 1,
            'recordsFiltered': all_instagrams_count,
            'recordsTotal': all_instagrams_count,
            'data': json_instagrams})
    else:
        raise Http404('URL解析エラー')


@csrf_exempt
@login_required(login_url='/login')
def create_instagram(request):
    media_id = request.POST['media_id']
    title = request.POST['title']
    url = request.POST['url']
    hash_tag = request.POST['hash_tag']
    regist_date = request.POST['regist_date']
    register = request.POST['register']
    project = request.POST['project']

    response_data = {}

    try:
        w_instagram = Media.objects.create(
            type=1,
            media_id=media_id,
            title=title,
            url=url,
            hash_tag=hash_tag,
            regist_date=regist_date,
            register_id=register,
            project_id=project)
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_CREATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def update_instagram(request):
    media_idx = request.POST.get('id', 0)
    media_id = request.POST.get('media_id', None)
    title = request.POST.get('title', None)
    url = request.POST.get('url', None)
    hash_tag = request.POST.get('hash_tag', None)
    regist_date = request.POST.get('regist_date', None)
    register = request.POST.get('register', None)
    project = request.POST.get('project', None)
    status = request.POST.get('status', None)

    response_data = {}

    try:
        w_instagram = Media.objects.get(id=media_idx)
    except Media.DoesNotExist:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_UPDATE'

        return JsonResponse(response_data)

    if media_id is not None:
        w_instagram.media_id = media_id

    if title is not None:
        w_instagram.title = title

    if url is not None:
        w_instagram.url = url

    if hash_tag is not None:
        w_instagram.hash_tag = hash_tag

    if regist_date is not None:
        w_instagram.regist_date = regist_date

    if register is not None:
        w_instagram.register_id = register

    if project is not None:
        w_instagram.project_id = project

    if status is not None:
        w_instagram.status = status

    try:
        w_instagram.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_MEDIA_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_instagram(request):
    if request.method == 'POST':
        media_idx = request.POST['id']

        json_instagram = {}

        try:
            w_instagram = Media.objects.get(id=media_idx)
        except Media.DoesNotExist:
            return JsonResponse(json_instagram)

        json_instagram = {
            'id': w_instagram.id,
            'media_id': w_instagram.media_id,
            'url': w_instagram.url,
            'hash_tag': w_instagram.hash_tag,
            'title': w_instagram.title,
            'project': w_instagram.project.id,
            'register': w_instagram.register.id,
            'regist_date': w_instagram.regist_date
        }

        return JsonResponse(json_instagram)
    else:
        raise Http404('URL解析エラー')


def parse_order(request):
    i = 0;
    orders = []
    order_str = ''
    while (1):
        col_idx = request.POST.get('order[' + str(i) + '][column]')
        if (col_idx == None):
            break

        col_name = request.POST.get('columns[' + col_idx + '][name]')
        dir = request.POST.get('order[' + str(i) + '][dir]')

        if col_name == 'number':
            col_name = 'id'

        one_order = col_name
        if (dir == 'desc'):
            one_order = '-' + col_name

        orders.append(one_order)
        i += 1

    return ', '.join(orders)


def handle_uploaded_file(file, file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, 'images/' + file_name)
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def delete_file(file_name):
    file_path = os.path.join(settings.MEDIA_ROOT, 'images/' + file_name)
    os.remove(file_path)