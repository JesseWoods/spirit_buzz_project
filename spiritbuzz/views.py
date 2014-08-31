from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from django.core.serializers import json
from django.template import RequestContext
from spiritbuzz.models import Category, Product, Order, OrderItem, ProductReview
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core import urlresolvers
from spiritbuzz.forms import ProductAddToCartForm, CheckoutForm, ProductReviewForm
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from spiritbuzz import search
from spiritbuzz import stats





def categoryList():
    return Category.objects.order_by('-name')




def index(request):

    context = RequestContext(request)

    categories = categoryList

    search_recs = stats.recommended_from_search(request)
    featured = Product.featured.all()[0:3]
    recently_viewed = stats.get_recently_viewed(request)
    view_recs = stats.recommended_from_views(request)



    return render_to_response('spiritbuzz/index.html', locals(), context)

def aboutus(request):
    categories = categoryList
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)

    return render_to_response('spiritbuzz/aboutus.html', context)



def category(request, category_slug):
    # Request our context from the request passed to us.
    categories = categoryList
    c = get_object_or_404(Category, slug = category_slug)

    products = c.product_set.all()
    page_title = c.name
    meta_keywords = c.meta_keywords
    meta_description = c.meta_description
    return render_to_response('spiritbuzz/category.html', locals(), context_instance = RequestContext(request))

from spiritbuzz import cart

def product(request, category_slug, product_slug):
    # Request our context from the request passed to us.

    p = get_object_or_404(Product, slug = product_slug)
    categories = categoryList
    page_title = p.name
    meta_keywords = p.meta_keywords
    meta_description = p.meta_description
    stats.log_product_view(request, p)
    product_reviews = ProductReview.approved.filter('date')
    review_form = ProductReviewForm()

    if request.method == 'POST':
        postdata = request.POST.copy()
        form = ProductAddToCartForm(request, postdata)
        if form.is_valid():

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            cart.add_to_cart(request)
            url = urlresolvers.reverse('show_cart')
            return HttpResponseRedirect(url)


        else:
            form = ProductAddToCartForm(request = request, label_suffix = ':')

        form.fields['product_slug'].widget.attrs['value'] = product_slug


        request.session.set_test_cookie()


    return render_to_response('spiritbuzz/product.html', locals(), context_instance = RequestContext(request))


from spiritbuzz.forms import UserForm, UserProfileForm

def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print(user_form.errors, profile_form.errors)

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    categories = categoryList
    # Render the template depending on the context.
    return render_to_response('spiritbuzz/register.html', locals(), context)

def user_login(request):
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)
    categories = categoryList
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/spiritbuzz/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your SpiritBuzz account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponseRedirect('/spiritbuzz/register/')

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('spiritbuzz/login.html', locals(), context)

from spiritbuzz import checkout


def show_cart(request, template_name = 'spiritbuzz/cart.html'):


    categories = categoryList
    if request.method == 'POST':
        postdata = request.POST.copy()
        if postdata['submit'] == 'Remove':
            cart.remove_from_cart(request)
        if postdata['submit'] == 'Update':
            cart.update_cart(request)
        if postdata['submit'] == 'Checkout':
            checkout_url = checkout.get_checkout_url(request)
            return HttpResponseRedirect(checkout_url)

    cart_items = cart.get_cart_items(request)
    page_title = 'Shopping Cart'
    cart_subtotal = cart.cart_subtotal(request)

    return render_to_response(template_name, locals(), context_instance = RequestContext(request))

def show_checkout(request, template_name = 'checkout/checkout.html'):
    categories = categoryList
    if cart.is_empty(request):
        cart_url = urlresolvers.reverse('show_cart')
        return HttpResponseRedirect(cart_url)

    if request.method =='POST':
        postdata = request.POST.copy()
        form = CheckoutForm(postdata)

        if form.is_valid():
            response = checkout.process(request)
            order_number = response.get('order_number', 0)
            error_message = response.get('message', 0)

            if order_number:
                request.session['order_number'] = order_number
                receipt_url = urlresolvers.reverse('checkout_receipt')
                return  HttpResponseRedirect(receipt_url)

        else:
            error_message = 'Correct the errors below.'

    else:
        form = CheckoutForm()

    page_title = 'Checkout'

    return render_to_response(template_name, locals(), context_instance = RequestContext(request))

def receipt(request, template_name = 'checkout/receipt.html'):
    categories = categoryList
    order_number = request.session.get('order_number')

    if order_number:
        order = Order.objects.filter(id = order_number)[0]
        order_items = OrderItem.objects.filter(order = order)
        del request.session['order_number']

    else:
        cart_url = urlresolvers.reverse('show_cart')
        return HttpResponseRedirect(cart_url)

    return render_to_response(template_name, locals(), context_instance = RequestContext(request))

def results(request, template_name = "spiritbuzz/results.html"):

    categories = categoryList
    q = request.GET.get('q', '')

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    matching = search.products(q).get('products')
    paginator = Paginator(matching, 9)

    try:
        results = paginator.page(page).object_list
    except (InvalidPage, EmptyPage):
        results = paginator.page(1).object_list

    search.store(request, q)
    page_title = 'Search Results for: '+ q

    return render_to_response(template_name, locals(), context_instance = RequestContext(request))

@login_required
def add_review(request):

    form = ProductReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit = False)
        slug = request.POST.get('slug')
        product = Product.active.get(slug = slug)
        review.user = request.user
        review.product = product
        review.save()
        template = "catalog/product_review.html"
        html = render_to_string(template, {'review': review})
        response = json.dumps({'success': 'True', 'html': html})

    else:
        html = form.errors.as_ul()
        response = simplejson.dumps({'success': 'False', 'html': html})

    return HttpResponse(response, content_type = 'application/javascript; charset = utf-8')




