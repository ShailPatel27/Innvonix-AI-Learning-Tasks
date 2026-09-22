import multiprocessing


def square(num):
    return num * num

if __name__ == "__main__":

    numbers = range(100000)

    with multiprocessing.Pool(processes=4) as pool:
        result = pool.map(square, numbers)

    print(result)