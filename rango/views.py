from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from rango.models import Category, Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm

from django.shortcuts import redirect
from django.urls import reverse


#Chapter 9

def register(request):
    registered = False
    
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            
            # Now we hash the password with the set_password method
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            
            # Since we need to set the user attribute ourselves,
            # we set commit=False. This delays saving the model

            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FLIES:
                profile.picture= request.FLIES['picture']
            
            # Now we save the UserProfile model instance.
            profile.save()
            
            # Update our variable to indicate that the template
            # registration was successful
            
            reqistered = True 
        else:
            # Prints problems to terminal
            print (user_form.errors, profile_forms.errors)
    else:
        # If not a HTTP POST, Render form using two modelForm instances. --- Blank form ready for user input
        
        user_form = UserForm()
        profile_form = USerProfileForm()
        
    return render(request, 'rango/register.html',context = {'user_form' : user_form, 'profile_form' : profile_form, 'registered' : registered})














###################################

def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None
        
    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect('/rango/')
    
    form = PageForm()
    
    
    if request.method == 'POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            if category:
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()
            return redirect(reverse('rango:show_category',
            kwargs={'category_name_slug':
            category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def show_category(request,category_name_slug):
    context_dict = {}
    try:
    # The .get() method returns one model instance or raises an exception.
        category =Category.objects.get(slug=category_name_slug)
    # Retrieve all of the associated pages.
    # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)
    # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
        # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)

def add_category(request):
    form = CategoryForm()
# A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now that the category is saved, we could confirm this.
            # For now, just redirect the user back to the index view.
            return redirect('/rango/')
    else:
        print(form.errors)
    # Will handle the bad form, new form, or no form supplied cases.
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

####################################

    
    
    
    
    
#Early Chapters
    
def index(request):
      
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}

    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('- views')[:5]
    
    context_dict = {}
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    return render(request, 'rango/index.html', context_dict)
     
def about(request):
    context_dict2 = {'name':'Adrian'}  
    return render(request, 'rango/about.html', context_dict2)
