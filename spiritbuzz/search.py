from spiritbuzz.models import SearchTerm, Product
from django.db.models import Q
from spiritbuzz import stats

STRIP_WORDS = ['a', 'an', 'and', 'by', 'for', 'from', 'in', 'no', 'not', 'of', 'on', 'or', 'that', 'the', 'to', 'with']


def store(request, q):

    if len(q) > 2:
        term = SearchTerm()
        term.q = q
        term.ip_address = request.META.get('REMOTE_ADDR')
        term.tracking_id = stats.tracking_id(request)
        term.user = None
        if request.user.is_authenticated():
            term.user = request.user

        term.save()

def products(search_text):

    words = _prepare_words(search_text)
    products = Product.active.all()
    results = {}
    results['products'] = []

    for word in words:
        products = products.filter(Q(name__icontains=word)|Q(description__icontains=word)|Q(sku__iexact=word)|Q(meta_description__icontains=word)|Q(meta_keywords__icontains=word))
        results['products'] = products

    return results

def _prepare_words(search_text):

    words = search_text.split()

    for common in STRIP_WORDS:
        if common in words:
            words.remove(common)

    return words[0:5]