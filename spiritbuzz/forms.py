from django import forms
from spiritbuzz.models import Product, Category, UserProfile, Order, SearchTerm, ProductReview
from django.contrib.auth.models import User
import datetime
import re



class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    #views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    #likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = Category

class ProductForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the name of the product.")
    description = forms.CharField(max_length=1000, help_text="Please enter a description.")
    size = forms.IntegerField()
    price = forms.DecimalField(help_text = "Please enter sale price:")
    picture = forms.ImageField()


    class Meta:
        # Provide an association between the ModelForm and a model
        model = Product

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.
        fields = ('name','description', 'size', 'price', 'picture')

class UserForm(forms.ModelForm):
    password = forms.CharField(label = "Password", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('picture',)

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product

    def clean_price(self):
        if self.cleaned_data['price'] <= 0:
            raise forms.ValidationError('Price must be greater than 0.')

        return self.cleaned_data['price']

class ProductAddToCartForm(forms.Form):
    #quantity = forms.IntegerField(widget = forms.TextInput(attrs = {'size': '2', 'value': '1', 'class': 'quantity', 'maxlength': '5'}), error_messages = {'invalid': 'Please enter a valid quantity.'}, min_value = 1)
    product_slug = forms.CharField(widget = forms.HiddenInput())

    def __init__(self, request = None, *args, **kwargs):
        self.request = request
        super(ProductAddToCartForm, self).__init__(*args, **kwargs)

    def clean(self):
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError("Cookies must be enabled.")

        return self.cleaned_data

def cc_expire_years():

    current_year = datetime.datetime.now().year
    years = range(current_year, current_year + 12)

    return [(str(x), str(x)) for x in years]

def cc_expire_months():

    months = []

    for month  in range(1, 13):
        if len(str(month)) == 1:
            numeric = '0' + str(month)
        else:
            numeric = str(month)

        months. append((numeric, datetime.date(2014, month, 1).strftime('%B')))

    return months

CARD_TYPES = (('Mastercard', 'Mastercard'), ('VISA', 'VISA'), ('AMEX', 'AMEX'), ('Discover', 'Discover'),)

STATE_ABBREVS =(( 'AL','AL'),('AK','AK'),('AZ','AZ'),('AR','AR'),('CA','CA'),('CO','CO'),('CT','CT'),('DE','DE'),('FL','FL'),('GA','GA'),('HI','HI'),('ID','ID'),('IL','IL'),('IN','IN'),('IA','IA'),('KS','KS'),('KY','KY'),('LA','LA'),('ME','ME'),('MD','MD'),('MA','MA'),('MI','MI'),('MN','MN'),('MS','MS'),('MO','MO'),('MT','MT'),('NE','NE'),('NV','NV'),('NH','NH'),('NJ','NJ'),('NM','NM'),('NY','NY'),('NC','NC'),('ND','ND'),('OH','OH'),('OK','OK'),('OR','OR'),('PA','PA'),('RI','RI'),('SC','SC'),('SD','SD'),('TN','TN'),('TX','TX'),('UT','UT'),('VT','VT'),('VA','VA'),('WA','WA'),('WV','WV'),('WI','WI'),('WY','WY'),)

def strip_non_numbers(data):

    non_numbers = re.compile('\D')

    return non_numbers.sub('', data)

def cardLuhnChecksumIsValid(card_number):

    sum = 0
    num_digits = len(card_number)
    oddeven = num_digits & 1

    for count in range(0, num_digits):
        digit = int(card_number[count])
        if not ((count & 1) ^ oddeven):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9
        sum = sum + digit

    return ((sum % 10) == 0)

class CheckoutForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):

        super(CheckoutForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['size'] = '30'

        #self.fields['shipping_state'].widget.attrs['size'] = '3'
        self.fields['shipping_state'].widget.attrs['size'] = '1'
        self.fields['shipping_zip'].widget.attrs['size'] = '6'
        #self.fields['billing_state'].widget.attrs['size'] = '3'
        self.fields['billing_state'].widget.attrs['size'] = '1'
        self.fields['billing_zip'].widget.attrs['size'] = '6'
        self.fields['credit_card_type'].widget.attrs['size'] = '1'
        self.fields['credit_card_expire_year'].widget.attrs['size'] = '1'
        self.fields['credit_card_expire_month'].widget.attrs['size'] = '1'
        self.fields['credit_card_cvv'].widget.attrs['size'] = '5'

    class Meta:
        model = Order
        exclude = ('satus', 'ip_address', 'user', 'transaction_id',)
    shipping_state = forms.CharField(widget = forms.Select(choices = STATE_ABBREVS))
    billing_state = forms.CharField(widget = forms.Select(choices = STATE_ABBREVS))
    credit_card_number = forms.CharField()
    credit_card_type = forms.CharField(widget = forms.Select(choices = CARD_TYPES))
    credit_card_expire_year = forms.CharField(widget = forms.Select(choices = cc_expire_years()))
    credit_card_expire_month = forms.CharField(widget = forms.Select(choices = cc_expire_months()))

    credit_card_cvv = forms.CharField()

def clean_credit_card_number(self):

    cc_number = self.cleaned_data['credit_card_number']
    stripped_cc_number = strip_non_numbers(cc_number)

    if not cardLuhnChecksumIsValid(stripped_cc_number):
        raise forms.ValidationError('The credit card you entered is invalid.')

def clean_phone(self):

    phone = self.cleaned_data['phone']
    stripped_phone = strip_non_numbers(phone)

    if len(stripped_phone) < 10:
        raise forms.ValidationError('Enter a valid phone number with area code. (e.g. 555-555-5555)')

    return self.cleaned_data['phone']

class SearchForm(forms.ModelForm):

    class Meta:
        model = SearchTerm

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        default_text = ''
        self.fields['q'].widget.attrs['value'] = default_text
        self.fields['q'].widget.attrs['onfocus'] = "if (this.value =='"+default_text+"')this.value = ''"

    include = ('q',)

class ProductReviewForm(forms.ModelForm):

    class Meta:
        model = ProductReview
        exclude = ('user', 'product', 'is_approved')