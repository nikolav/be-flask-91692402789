from sqlalchemy.orm import joinedload
from flask_app import db

from models.products import Products

from config.graphql.init import query


@query.field('productsTotalAmountOrdered')
def resolve_productsTotalAmountOrdered(_obj, _info, pid):
  amount = 0
  
  try:
    p      = db.session.get(Products, pid)
    amount = p.total_amount_ordered()
    
  except Exception as err:
    raise err

  return { 'amount': amount }
