import os


def populate():
    whiskey_cat = add_cat('Whiskies','delicious whiskeys','whiskey, stuff', 'good, good, good')

    add_product(cat=whiskey_cat,name="Old Overholt",sku = 908767, description = "blahblahblah", price = 99.99, picture = 'products/urkel.jpg',views = 100, meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=whiskey_cat, name="Jack Daniels", sku = 98765, description = "blahblahblah", price = 99.99, picture = 'products/urkel.jpg', views = 10,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=whiskey_cat, name="Old Grand Dad", sku = 94321, description = "blahblahblah", price = 99.99, picture = 'products/urkel.jpg', views = 100,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    vodka_cat = add_cat("Vodka", 'delicious vodkas','whiskey, stuff', 'good, good, good')

    add_product(cat=vodka_cat, name="Absolut", sku = 98543, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 100, meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=vodka_cat, name="Smirnoff",sku = 43216, description = "blahblahblah", price = 99.99, picture = 'products/urkel.jpg', views = 18,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=vodka_cat, name="Ketel One", sku = 90876, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg',  views = 1000,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    gin_cat = add_cat("Gin",'delicious gin','whiskey, stuff', 'good, good, good' )

    add_product(cat=gin_cat,name="Tanqueray", sku = 98546, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 10, meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=gin_cat, name = "Beefeater", sku = 65478, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 100,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    tequila_cat = add_cat("tequila", 'delicious tequilas','whiskey, stuff', 'good, good, good')

    add_product(cat=tequila_cat, name="Jose Cuervo", sku = 87632, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 100,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=tequila_cat, name="Patron Silver", sku = 56743, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 1,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    rum_cat = add_cat("Rum", 'delicious rum','whiskey, stuff', 'good, good, good')

    add_product(cat=rum_cat, name="Bacardi", sku = 76854, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 100,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    add_product(cat=rum_cat, name="Ron Zacapa", sku = 87965, description = "blahblahblah", price = 99.99,picture = 'products/urkel.jpg', views = 10,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')

    liqueur_cat = add_cat('Liqueur', 'sweet crap','whiskey, stuff', 'good, good, good')

    add_product(cat = liqueur_cat, name = 'Saint Germain', sku = 78967, description = 'hgfgfgrcdd', price = 78.56, picture = 'products/knifedog.jpg', views = 9,  meta_keywords = 'ooo,hh,nn', meta_description = 'pootyyut')


    # Print out what we have added to the user.
    for c in Category.objects.all():
        for p in Product.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))

def add_product(cat, name, sku, description, price, picture, views, meta_keywords, meta_description):
    p = Product.objects.get_or_create(category=cat, name = name,slug = generate_slug(name), sku = sku, description = description, price = price, picture = picture, views=views, meta_keywords = meta_keywords, meta_description = meta_description)[0]
    return p

def add_cat(name, description, meta_keywords, meta_description):
    c = Category.objects.get_or_create(name=name, slug = generate_slug(name), description = description, meta_keywords = meta_keywords, meta_description = meta_description)[0]
    return c
def generate_slug(name):

    return name.replace(' ', '-')


# Start execution here!
if __name__ == '__main__':
    print("Starting SpiritBuzz population script...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spirit_buzz_project.settings')
    from spiritbuzz.models import Category, Product
    populate()
