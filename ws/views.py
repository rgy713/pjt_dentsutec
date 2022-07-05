from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.db import connection
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
import calendar
from django.db.models import Max, Min, Count, F
from backend.models import Country, Category, Project, Media, Segment, Company, Client, User_setting
# Create your views here.


@csrf_exempt
@login_required(login_url='/login')
def list_country(request):
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
def list_category(request):
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
def list_segment(request):
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
def list_company(request):
    w_segment = int(request.POST.get('segment', 0))
    w_keyword = request.POST.get('keyword', '')
    company_list = Company.objects.filter(status__exact=1)
    if w_segment > 0:
        company_list = company_list.filter(segment__exact=w_segment)

    if len(w_keyword) > 0:
        company_list = company_list.filter(company_name__icontains=w_keyword)

    json_companies = []
    for w_company in company_list:
        json_company = {
            'id': w_company.id,
            'company_name': w_company.company_name,
            'segment': w_company.segment.id
        }
        json_companies.append(json_company)

    return JsonResponse({
        'type': 'S_OK',
        'content': json_companies
    })


@csrf_exempt
@login_required(login_url='/login')
def list_client(request):
    w_country = int(request.POST.get('country', 0))
    w_keyword = request.POST.get('keyword', '')

    client_list = Client.objects.filter(status__exact=1)
    if w_country > 0:
        client_list = client_list.filter(register__profile__country__exact=w_country)

    if len(w_keyword) > 0:
        client_list = client_list.filter(client_name__icontains=w_keyword)

    json_clients = []
    for w_client in client_list:
        client_name = w_client.client_name
        if len(client_name) > 35:
            client_name = client_name[0:35] + "..."
        json_client = {
            'id': w_client.id,
            'client_name': client_name,
            'company': w_client.company.company_name,
            'country': w_client.register.profile.country.id
        }
        json_clients.append(json_client)

    return JsonResponse({
        'type': 'S_OK',
        'content': json_clients
    })


@csrf_exempt
@login_required(login_url='/login')
def list_segment_client(request):
    w_segment = int(request.POST.get('segment', 0))
    name_limit = int(request.POST.get('name_limit', 0))

    project_list = Project.objects.filter(status__exact=1, client__isnull=False)

    if w_segment > 0:
        project_list = project_list.filter(segment_id=w_segment)

    project_list = project_list.values('client').annotate(Count('id'))

    json_clients = []
    for w_project in project_list:
        w_client = Client.objects.get(id=w_project['client'])

        client_name = w_client.client_name
        if len(client_name) > 10 and name_limit > 0:
            client_name = client_name[0:10] + "..."

        json_client = {
            'id': w_client.id,
            'client_name': client_name,
            'company': w_client.company.company_name
        }
        json_clients.append(json_client)

    return JsonResponse({
        'type': 'S_OK',
        'content': json_clients
    })


@csrf_exempt
@login_required(login_url='/login')
def list_media(request):
    media_type = request.POST.get('type', None)
    length = int(request.POST.get('length', 100))
    project_idx = request.POST.get('project_idx', None)

    orders = '-regist_date'

    media_list = Media.objects.filter(status__exact=1)

    if project_idx is not None:
        media_list = media_list.filter(project__id=project_idx)

    if media_type is not None:
        media_list = media_list.filter(type__exact=media_type)

    media_list = media_list.order_by(orders)[0:length]

    json_medias = []
    for w_media in media_list:
        json_media = {
            'id': w_media.id,
            'title': w_media.title,
            'project': w_media.project.id,
            'project_name': w_media.project.project_name,
            'type': w_media.type,
            'url': w_media.url,
            'thumb': w_media.thumb,
            'country': w_media.project.register.profile.country.country_name,
            'client': w_media.project.client.client_name if w_media.project.client is not None else '',
            'company': w_media.project.client.company.company_name if w_media.project.client is not None else '',
            'regist_date': datetime.strftime(datetime.fromtimestamp(calendar.timegm(w_media.regist_date.timetuple())), "%Y/%m/%d")
        }
        json_medias.append(json_media)

    return JsonResponse({
        'type': 'S_OK',
        'content': json_medias
    })


@csrf_exempt
@login_required(login_url='/login')
def list_project(request):
    country_id = request.POST.get('country_id', None)
    category_idx = request.POST.get('category_idx', None)
    length = int(request.POST.get('length', 0))
    w_segment = int(request.POST.get('segment', 0))
    w_company = int(request.POST.get('company', 0))
    w_client = int(request.POST.get('client', 0))

    media_list = Media.objects.filter(status__exact=1).order_by('-regist_date').values('project').annotate(regist_date=Max('regist_date'))

    exclude_countries = request.POST.get('exclude_countries', [])
    if len(exclude_countries) > 0:
        exclude_countries = exclude_countries.split(',')
        exclude_countries = [int(i) for i in exclude_countries]

    exclude_categories = request.POST.get('exclude_categories', [])
    if len(exclude_categories) > 0:
        exclude_categories = exclude_categories.split(',')
        exclude_categories = [int(i) for i in exclude_categories]

    media_list = media_list.filter(
        project__status__exact=1, project__project_name__isnull=False
    ).exclude(
        project__register__profile__country__in=exclude_countries,
    ).exclude(
        project__category__in=exclude_categories,
    )

    w_user = request.user
    w_user_setting, created = User_setting.objects.get_or_create(user_id=w_user.id)
    user_exclude_segments = w_user_setting.segments
    user_exclude_companies = w_user_setting.companies
    user_exclude_countries = w_user_setting.countries

    user_exclude_segments = ''
    if len(user_exclude_segments) > 0:
        user_exclude_segments = user_exclude_segments.split(',')
        user_exclude_segments = [int(i) for i in user_exclude_segments]
        media_list = media_list.exclude(
            project__segment__in=user_exclude_segments
        )

    if len(user_exclude_companies) > 0:
        user_exclude_companies = user_exclude_companies.split(',')
        user_exclude_companies = [int(i) for i in user_exclude_companies]
        media_list = media_list.exclude(
            project__client__in=user_exclude_companies
        )

    if len(user_exclude_countries) > 0:
        user_exclude_countries = user_exclude_countries.split(',')
        user_exclude_countries = [int(i) for i in user_exclude_countries]
        media_list = media_list.exclude(
            project__register__profile__country__in=user_exclude_countries
        )

    if country_id is not None:
        media_list = media_list.filter(project__register__profile__country__country_id=country_id)

    if category_idx is not None:
        media_list = media_list.filter(project__category__id=category_idx)

    if w_segment > 0:
        media_list = media_list.filter(project__segment__exact=w_segment)

    if w_company > 0:
        media_list = media_list.filter(project__client__company__exact=w_company)

    if w_client > 0:
        media_list = media_list.filter(project__client__exact=w_client)

    json_projects = []
    for w_info in media_list:
        w_media = Media.objects.filter(project_id=w_info['project'], regist_date=w_info['regist_date']).first()
        w_project = Project.objects.get(id=w_info['project'])
        project_name = w_project.project_name
        if len(project_name) > 16:
            project_name = project_name[0:16] + "..."
        company_name = w_project.client.company.company_name if w_project.client is not None else ''
        if len(company_name) > 10:
            company_name = company_name[0:10] + "..."

        json_project = {
            'id': w_project.id,
            'project_name': project_name,
            'client': w_project.client.id if w_project.client is not None else '',
            'client_name': w_project.client.client_name if w_project.client is not None else '',
            'start_date': w_project.start_date,
            'end_date': w_project.end_date,
            'country': w_project.register.profile.country.country_name,
            'company': company_name,
            'type': w_media.type,
            'url': w_media.url,
            'thumb': w_media.thumb,
            'regist_date': datetime.strftime(datetime.fromtimestamp(calendar.timegm(w_media.regist_date.timetuple())), "%Y/%m/%d")
        }
        json_projects.append(json_project)


    return JsonResponse({
        'type': 'S_OK',
        'content': json_projects
    })


@csrf_exempt
@login_required(login_url='/login')
def get_project(request):
    project_idx = request.GET.get('id', 0)

    json_project = {}

    try:
        w_project = Project.objects.get(id=project_idx)
    except Project.DoesNotExist:
        return JsonResponse(json_project)

    json_project = {
        'id': w_project.id,
        'project_id': w_project.project_id,
        'project_name': w_project.project_name,
        'client': w_project.client.client_name if w_project.client is not None else '',
        'start_date': datetime.strftime(w_project.start_date, "%Y/%m/%d"),
        'end_date': datetime.strftime(w_project.end_date, "%Y/%m/%d"),
        'country': w_project.register.profile.country.country_name,
        'category': w_project.category.category_name,
        'outline': w_project.outline,
        'result': w_project.result
    }

    return JsonResponse({
        'type': 'S_OK',
        'content': json_project
    })


@csrf_exempt
@login_required(login_url='/login')
def update_user_setting(request):
    w_user = request.user
    user_segments = request.POST.get('segments', None)
    user_companies = request.POST.get('companies', None)
    user_countries = request.POST.get('countries', None)

    response_data = {}

    w_user_setting, created = User_setting.objects.get_or_create(user_id=w_user.id)

    if user_segments is not None:
        w_user_setting.segments = user_segments

    if user_companies is not None:
        w_user_setting.companies = user_companies

    if user_countries is not None:
        w_user_setting.countries = user_countries

    try:
        w_user_setting.save()
    except:
        response_data['type'] = 'E_FAIL'
        response_data['content'] = 'ERR_SETTING_UPDATE'

        return JsonResponse(response_data)

    response_data['type'] = 'S_OK'

    return JsonResponse(response_data)


@csrf_exempt
@login_required(login_url='/login')
def get_user_setting(request):
    w_user = request.user
    w_user_setting, created = User_setting.objects.get_or_create(user_id=w_user.id)
    user_exclude_segments = w_user_setting.segments
    user_exclude_companies = w_user_setting.companies
    user_exclude_countries = w_user_setting.countries

    json_user_setting = {
        'segments': user_exclude_segments,
        'companies': user_exclude_companies,
        'countries': user_exclude_countries
    }

    return JsonResponse({
        'type': 'S_OK',
        'content': json_user_setting
    })


def getCategoryList(request):
    cursor = connection.cursor()
    query_string = "SELECT id, category_name FROM t_category WHERE status = 1"
    with connection.cursor() as cursor:
        cursor.execute(query_string)
        categoryList = dictfetchall(cursor)

    return HttpResponse(json.dumps(categoryList), content_type="application/json")


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]