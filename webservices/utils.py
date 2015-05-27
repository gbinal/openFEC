from webservices import paging
from webservices import sorting


def fetch_page(query, kwargs, model=None, clear=False):
    query = sorting.sort(query, kwargs['sort'], model=model, clear=clear)
    paginator = paging.SqlalchemyPaginator(query, kwargs['per_page'])
    return paginator.get_page(kwargs['page'])
