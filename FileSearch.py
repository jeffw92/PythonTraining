import os, glob

#os.chdir("C:\Users\b7719\Pictures")

#for file in glob.glob("*.jpg"):
#    print(file)


## Fizz Buzz
#for num in xrange(1,101):
#    if num % 5 == 0 and num % 3 == 0:
#        print "FizzBuzz"
#    elif num % 3 == 0:
#        print "Fizz"
#    elif num % 5 == 0:
#        print "Buzz"
#    else:
#        print num

## Fibonacci Sequence
#a, b = 0, 1
#for i in xrange(0,10):
#    print a
#    a, b = b, a + b

## Fibonacci Generator
#def fib(num):
#    a,b = 0,1
#    for i in xrange(0, num):
#        yield"{}: {}".format(i+1, a)
#        a,b = b, a + b

#for item in fib(10):
#    print item

## Lists
#my_list = [ 10,20,30,40,50]
#for i in my_list:
#    print i

## List comprehensions
##    Give me each number in a list squared
#squares = [num * num for num in my_list]
#print squares

## Tuples
#my_tup = (1,2,3,4,5,6,7,8,9,10)
#for i in my_tup:
#    print i

## Dict
#my_dict = {'name':'Scamp', 'age':'9', 'occupation': 'My Dog'}
#for key,val in my_dict.iteritems():
#    print "My {} is {}".format(key,val)

## Set
#my_set = {10,20,30,40,50,10,20,30,40,50}
#for i in my_set:
#    print i

# Try/Accept

# With

# OOP
class Person(object):
    def __init__(self,name):
        self.name = name

    def reveal_identity(self):
        print "My name is {}".format(self.name)

class SuperHero(Person):
    def __init__(self, name, hero_name):
        super(SuperHero, self).__init__(name)
        self.hero_name = hero_name

    def reveal_identity(self):
        super(SuperHero, self).reveal_identity()
        print "...And I am {}".format(self.hero_name)

jeff = Person('Jeff')
jeff.reveal_identity()

wade = SuperHero('Wade Wilson', 'Deadpool')
wade.reveal_identity()

# SQL Alchemy
