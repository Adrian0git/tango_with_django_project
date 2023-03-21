from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import Http404
from datetime import datetime

from rango.models import Category, Page, UserProfile

from rango.forms import CategoryForm, PageForm
from rango.forms import UserForm, UserProfileForm

from django.urls import reverse
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from rango.bing_search import run_query
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User

def goto_url():
        if request.method == 'GET':
            page_id = request.GET.get('page_id')
            try:
                selected_page = Page.objects.get(id=page_id)
            except Page.DoesNotExist:
                return redirect(reverse('rango:index'))
            selected_page.views = selected_page.views + 1
            selected_page.save()
            return redirect(selected_page.url)
        return redirect(reverse('rango:index'))

def search_denial():
    # Take the user back to the homepage.
    return redirect(reverse('rango:restricted'))

###Chapter 13
def search_bar(request):
    result_list = []
    query = ''
    
    if request.method == 'POST':
        #Until You have made a key You will be sent to this page - if deleted without key, a 404 page shows
        return search_denial() # Delete when key is made 
        
        
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
    
    return render(request, 'rango/search.html', {'result_list': result_list, 'query': query})


####Chapter 10

def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, then the default value of 1 is used.
    visits = int(request.COOKIES.get('visits', '1'))
    
    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
    
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
    '%Y-%m-%d %H:%M:%S')
    
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits


#Chapter 9

@login_required
def restricted(request):
    context_dict ={'bold': 'Restricted Page'}
    return render(request, 'rango/restricted.html', context_dict)
    
    #decomissioned from chapter 11 #################################
#
#@login_required
#def user_logout(request):
#    # Since we know the user is logged in, we can now just log them out.
#    logout(request)
#    # Take the user back to the homepage.
#    return redirect(reverse('rango:index'))
#
#
#
#def user_login(request):
## If the request is a HTTP POST, try to pull out the relevant information.
#    if request.method == 'POST':
#        # We use request.POST.get('<variable>') as opposed
#        # to request.POST['<variable>'], because the
#        # request.POST.get('<variable>') returns None if the
#        # value does not exist, while request.POST['<variable>']
#        # will raise a KeyError exception.
#        username = request.POST.get('username')
#        password = request.POST.get('password')
#
#        user = authenticate(username=username, password=password)
#        # If we have a User object, the details are correct.
#        # If None (Python's way of representing the absence of a value), no user
#        # with matching credentials was found.
#        if user:
#            if user.is_active:
#            # We'll send the user back to the homepage.
#                    login(request, user)
#                    return redirect(reverse('rango:index'))
#            else:
#            # An inactive account was used - no logging in!
#                    return HttpResponse("Your Rango account is disabled.")
#        else:
#            # Bad login details were provided. So we can't log the user in.
#                print(f"Invalid login details: {username}, {password}")
#                return HttpResponse("Invalid login details supplied.")
#    # The request is not a HTTP POST, so display the login form.
#    # This scenario would most likely be a HTTP GET.
#    else:
#    # blank dictionary object...
#        return render(request, 'rango/login.html')


#def register(request):
#    registered = False
#    
#    if request.method == 'POST':
#        user_form = UserForm(request.POST)
#        profile_form = UserProfileForm(request.POST)
#        if user_form.is_valid() and profile_form.is_valid():
#            user = user_form.save()
#            user.set_password(user.password)
#            user.save()
#            # Since we need to set the user attribute ourselves,
#            # we set commit=False. This delays saving the model
#            profile = profile_form.save(commit=False)
#            profile.user = user
#            
#            if 'picture' in request.FILES:
#                profile.picture= request.FILES['picture']
#            
#            profile.save()        
#            registered = True 
#        else:
#            # Prints problems to terminal
#            print (user_form.errors, profile_forms.errors)
#    else:
#        # If not a HTTP POST, Render form using two modelForm instances. --- Blank form ready for user input
#        user_form = UserForm()
#        profile_form = UserProfileForm()
#        
#    return render(request, 'rango/register.html',context = {'user_form' : user_form, 'profile_form' : profile_form, 'registered' : registered})

###################################


#chapter 6-7#######
@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        
    # You cannot add a page to a Category that does not exist.
    if category is None:
        return redirect(reverse('rango:index'))
    
    form = PageForm()
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def show_category(request,category_name_slug):
    context_dict = {}
    
    try:
       # The .get() method returns one model instance or raises an exception.
        category =Category.objects.get(slug=category_name_slug)
       # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category).order_by('-views')

        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None
        
    if request.method == 'POST':
        #404 error until key implemented
        if request.method == 'POST':
            query = request.POST['query'].strip()
            if query:
                context_dict['result_list'] = run_query(query)
                
    return render(request, 'rango/category.html', context=context_dict)

@login_required 
def add_category(request):
    form = CategoryForm()
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

####################################

    
#Early Chapters
    
def index(request):

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    context_dict = {}
    context_dict['boldmessage']= 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    
    # Obtain our Response object early so we can add cookie information.
    response = render(request, 'rango/index.html', context=context_dict)

    # Call the helper function to handle the cookies
    visitor_cookie_handler(request)
    
    return render(request, 'rango/index.html', context_dict)
     
def about(request):
    context_dict2 = {}
    context_dict2 = {'name':'Adrian'}  
    visitor_cookie_handler(request)
    context_dict2['visits'] = request.session['visits']
    
    return render(request, 'rango/about.html', context=context_dict2)
