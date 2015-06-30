import sqlalchemy as sa

from webservices import paging
from webservices import sorting


def fetch_page(query, kwargs, model=None, clear=False):
    query = sorting.sort(query, kwargs['sort'], model=model, clear=clear)
    paginator = paging.SqlalchemyPaginator(query, kwargs['per_page'])
    return paginator.get_page(kwargs['page'])


def extend(*dicts):
    ret = {}
    for each in dicts:
        ret.update(each)
    return ret


def search_text(query, column, text):
    vector = ' & '.join(text.split())
    vector = sa.func.concat(vector, ':*')
    return query.filter(
        column.match(vector)
    ).order_by(
        sa.desc(
            sa.func.ts_rank_cd(
                column,
                sa.func.to_tsquery(vector)
            )
        )
    )


def make_pdf_url(image_number):
    return 'http://docquery.fec.gov/pdf/{0}/{1}/{1}.pdf'.format(
        str(image_number)[-3:],
        image_number,
    )

def pdf_by_form(image_number, form_type, report_year):
    if report_year is None or form_type is None:
        return None
    elif form_type in ['F3X', 'F3P'] and report_year > 1993:
        return make_pdf_url(image_number)
    elif report_year > 2000:
        return make_pdf_url(image_number)
    else:
        return None


