import pickle
import inspect
import shelve

HARVEST="test"

def build_key(f):
    return inspect.getmodule(f).__name__ + f.__name__

def preserve(f, args, kwargs, result):    
    key = build_key(f)
    store = shelve.open("./harvest.out")

    if key not in store:
        store[key] = [(args, kwargs, result)]
    else:
        temp = store[key]
        temp.append( (args, kwargs, result) )
        store[key] = temp 

def restore(f):
    key = build_key(f)
    store = shelve.open("./harvest.out")

    if key in store:
        result = (None, store[key])
        return result    
    return ("Sorry, couldn't find your key :" + key, None)
    
def harvest(f):
    def wrapper(*args, **kwargs):
        options = ["off", "on", "test"]
        if HARVEST not in options: 
            print "Please assign HARVEST one of the following: ",
            print options
            print "It's currently set to "
            print HARVEST
            return f(*args, **kwargs)

        if HARVEST is "off": # do nothing
            return f(*args, **kwargs)

        if HARVEST is "test": # look up the test data, and test again      
            key = build_key(f)
            msg, units = restore(f)

            if msg != None:
                print msg
                return f(*args, **kwargs)
        
            for unit in units:
                a, kw, res = unit
                print "Testing: ", key, a, kw, res
                try:
                    if f(*a, **kw) == res:
                        print "PASSED"
                    else:
                        print "FAILED"
                        print "Expecting: ", res
                        print "Got:       ", f(*a, **kw)
                except:
                    print "FAILED"
            return f(*args, **kwargs)

        if HARVEST is "on": # add this new data to the tests
            print "got a", args, kwargs
            result = f(*args, **kwargs)
            preserve( f, args, kwargs, result )
            return result
    return wrapper
                
@harvest
def square(x):
    return x*x 
#square = harvest(square)

if __name__ == "__main__":
    for i in range(100):
        square(i)
