_randomi = 0
def randint(a,b):
  global _randomi
  nonrando = [3,14,8]
  result = nonrando[_randomi]
  _randomi = _randomi + 1
  return result
