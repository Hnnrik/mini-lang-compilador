x = 5
resultado = 1
def calcular(n):
    if (n > 0):
        return (n * calcular((n - 1)))
    return 1
print("Calculando Fatorial de 5:")
resultado = calcular(x)
print(resultado)