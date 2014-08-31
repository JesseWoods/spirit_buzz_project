from django.db import models
# Import the Category model
from django.contrib.auth.models import User
import decimal

class ActiveCategoryManager(models.Manager):
    def get_query_set(self):
        return super(ActiveCategoryManager, self).get_query_set().filter(is_active = True)

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length = 50, unique = True, help_text = 'Unique value for category page URL, created from name.')
    description = models.TextField()
    is_active = models.BooleanField(default = True)
    meta_keywords = models.CharField('Meta Keywords', max_length = 255, help_text = 'Comma delimited set of SEO keywords for meta tag')
    meta_description = models.CharField('Meta Description', max_length = 255, help_text = 'Content for description meta Tag')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = models.Manager()
    active = ActiveCategoryManager()

    class Meta:
        db_table = 'categories'
        ordering = ['-created_at']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

@models.permalink
def get_absolute_url(self):
    return ('category', (), {'category_slug': self.slug})

class ActiveProductManager(models.Manager):
    def get_query_set(self):
        return super(ActiveProductManager, self).get_query_set().filter(is_active = True)

class FeaturedProductManager(models.Manager):
    def all(self):
        return super(FeaturedProductManager, self).all().filter(is_active = True).filter(is_featured = True)


class Product(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField(max_length=128, unique = True)
    slug = models.SlugField(max_length = 128, unique = True, help_text = 'Unique value for product page url, created from name.')
    sku = models.CharField(max_length = 50, unique = True)
    description = models.TextField()
    size = models.IntegerField(default = 750)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    old_price = models.DecimalField(max_digits=7, decimal_places=2, blank = True, default = 0.00)
    picture = models.ImageField(upload_to='products', blank=True)
    is_active = models.BooleanField(default = True)
    is_featured = models.BooleanField(default = True)
    meta_keywords = models.CharField('Meta Keywords', max_length = 255, help_text = 'Comma delimited set of SEO keywords for meta tag')
    meta_description = models.CharField('Meta Description', max_length = 255, help_text = 'Content for description meta Tag')
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    views = models.IntegerField(default=0)
    objects = models.Manager()
    active = ActiveProductManager()
    featured = FeaturedProductManager()

    class Meta:
        db_table = 'products'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('product', (), {'product_slug': self.slug})

    @property
    def sale_price(self):
        if self.old_price > self.price:
            return self.price
        else:
            return None

    def cross_sells_hybrid(self):

        from spiritbuzz.models import Order, OrderItem
        from django.contrib.auth.models import User
        from django.db.models import Q

        orders = Order.objects.filter(orderitem__product = self)
        users = User.objects.filter(order__orderitem__product = self)
        items = OrderItem.objects.filter(Q(order__user__in = users)).exclude(product = self)
        products = Product.active.filter(orderitem__in = items).distinct()

        return products

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    user = models.OneToOneField(User)

    # The additional attributes we wish to include.
    #isAdmin = models.BooleanField()
    picture = models.ImageField(upload_to='profile_images', blank=True)

    # Override the __unicode__() method to return out something meaningful!
    def __str__(self):
        return self.user.username

class CartItem(models.Model):
    cart_id = models.CharField(max_length = 50)
    date_added = models.DateTimeField(auto_now_add = True)
    quantity = models.IntegerField(default = 1)
    product = models.ForeignKey('spiritbuzz.Product', unique = False)

    class Meta:
        db_table = 'cart_items'
        ordering = ['date_added']

    @property
    def total(self):
        return self.quantity * self.product.price

    @property
    def name(self):
        return self.product.name

    @property
    def price(self):
        return self.product.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()

    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()

class Order(models.Model):

    SUBMITTED = 1
    PROCESSED = 2
    SHIPPED = 3
    CANCELLED = 4

    ORDER_STATUSES = ((SUBMITTED, 'Submitted'),(PROCESSED, 'Processed'),(SHIPPED, 'Shipped'),(CANCELLED, 'Cancelled'),)

    date = models.DateTimeField(auto_now_add = True)
    status = models.IntegerField(choices = ORDER_STATUSES, default = SUBMITTED)
    ip_address = models.IPAddressField()
    last_updated = models.DateTimeField(auto_now = True)
    user = models.ForeignKey(User, null = True)
    transaction_id = models.CharField(max_length = 20)

    email = models.EmailField(max_length = 50)
    phone = models.CharField(max_length = 20)

    shipping_name = models.CharField(max_length = 50)
    shipping_address_1 = models.CharField(max_length = 50)
    shipping_address_2 = models.CharField(max_length = 50, blank = True)
    shipping_city = models.CharField(max_length = 50)
    shipping_state = models.CharField(max_length = 2)
    shipping_country = models.CharField(max_length = 50)
    shipping_zip = models.CharField(max_length = 10)

    billing_name = models.CharField(max_length = 50)
    billing_address_1 = models.CharField(max_length = 50)
    billing_address_2 = models.CharField(max_length = 50, blank = True)
    billing_city = models.CharField(max_length = 50)
    billing_state = models.CharField(max_length = 2)
    billing_country = models.CharField(max_length = 50)
    billing_zip = models.CharField(max_length = 10)

    def __str__(self):
        return 'Order #:' + str(self.id)

    @property
    def total(self):
        total = decimal.Decimal('0.00')
        order_items = OrderItem.objects.filter(order = self)

        for item in order_items:
            total += item.total

        return total

class OrderItem(models.Model):

    product = models.ForeignKey(Product)
    quantity = models.IntegerField(default = 1)
    price = models.DecimalField(max_digits = 9, decimal_places = 2)
    order = models.ForeignKey(Order)

    @property
    def total(self):
        return self.quantity * self.price

    @property
    def name(self):
        return self.product.name

    @property
    def sku(self):
        return self.product.sku

    def __str__(self):
        return self.product.name + '(' + self.product.sku + ')'

class SearchTerm(models.Model):

    q = models.CharField(max_length = 50)
    search_date = models.DateTimeField(auto_now_add = True)
    ip_address = models.IPAddressField()
    user = models.ForeignKey(User, null = True)
    tracking_id = models.CharField(max_length = 50, default = '')

    def __str__(self):
        return self.q

class PageView(models.Model):

    class Meta:
        abstract = True

    date = models.DateTimeField(auto_now = True)
    ip_address = models.IPAddressField()
    user = models.ForeignKey(User, null = True)
    tracking_id = models.CharField(max_length = 50, default = '')

class ProductView(PageView):
    product = models.ForeignKey(Product)

class ActiveProductReviewManager(models.Manager):

    def all(self):
        return super(ActiveProductReviewManager, self).all().filter(is_approved = True)

class ProductReview(models.Model):

    RATINGS = [(5,5),(4,4),(3,3),(2,2),(1,1),]
    product = models.ForeignKey(Product)
    user = models.ForeignKey(User)
    title = models.CharField(max_length = 50)
    date = models.DateTimeField(auto_now_add = True)
    rating = models.PositiveSmallIntegerField(default = 5, choices = RATINGS)
    is_approved = models.BooleanField(default = True)
    content = models.TextField()
    objects = models.Manager()
    approved = ActiveProductReviewManager()
