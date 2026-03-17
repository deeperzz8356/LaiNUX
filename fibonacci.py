# Fibonacci sequence calculator

def fibonacci(n):
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    return fib_sequence[:n]

# Calculate first 10 Fibonacci numbers
first_10_fib = fibonacci(10)
print(first_10_fib)