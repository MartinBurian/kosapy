kosapy
======

kosapy is a python client library for KosAPI, a REST API created to access the study information system KOS on CTU Prague.

It is based on the implementation ideas of the [*siesta project*](https://github.com/scastillo/siesta). It is left to the user to take care of calling the API in a valid way as the library has no bindings to the API structure. It could even (after slight modifications) be used for nearly any REST API. The only presumptions made about the XML is organization of data into an ATOM feed and cross-referencing using xlink:href attribute.

Kosapy depend on requests and requests-cache (both best installed using pip) and is guaranteed to work with python 3.3. Earlier version support depends mainly on the libraries, any python 3+ should be fine.

The cache will write to the current directory into file kosapy_cache.sqlite. The cache lifetime is 24h, earase by deleting the file.

Start by seeing the examples.py and typing:

    from koapy import Kosapy
    k=Kosapy(url, ('username', 'password'))

Resources
---------
A resource is referenced by k.resource.sub.ssub, e.g.

    k.students.buriama8.enrolledCourses

If the resource is not a valid python identifier, use the get method to reference it:

    k.resource.get("invalid:recource-name").ssub

The resource contents are fetched by calling or iterating over the resource. Fetch one entry:

    entry=k.students.buriama8()
    entry2=k.students.get("buriama8")()

Iterate over all entries (paging taken into account):

    for entry in k.students.buriama8.enrolledCourses:
        do stuff()

URL parameters are specified as kwargs:

    for entry in k.courses(query="code=gt=A4;code=lt=A5", sem="B131"):
        do stuff with OI-only course entries in semester B131
        
The result of calling with kwargs is a resource, so in the rare occasion you want only one entry of a filtered resource, you need to call for it:

    k.courses(sem="B131")()

Fields
------
In the entry you access the fields (=tags) in the atom:content hierarchically. Accessing the day in parallel entry is

    for parallel in k.parallels:
        parallel.timetableSlot.day

If the field names are not valid python identifiers, use the get() method instead:

    parallel.get("timetableSlot").day
    
The returned field is always iterable:

    for slot in parallel.timetableSlot:
        print(slot.day)

When there are more tags with the same path (e.g. parallel.teacher), the result is a list; when the tag is only one, it
can be used directly:

    parallel.semester.code

Acessing a field that is not present returns False:

    parallel.semester.weather # returns False

The rule of the thumb is: When you are not sure if the tag is present, check first. When you are sure there will be precisely one tag, use it directly. When there is even a slight
possibility that there will be more, iterate as it's guaranteed to work.

Advanced selection: get() supports filtering:

    parallel.get("teacher", rel="stylesheet")
selects all teachers with rel="stylesheet" attribute.


Get field content by calling:

    parallel.code()
    
Get filed attribute by calling too:

    parallel.course("xlink:href)

kosapy deals with xlink references for you, so listing enrolled exam dates is as simple as

    for registration in k.students.buriama8.registeredExams:
        print registration.exam.startDate()

The referenced resource is fetched for you and the resulting entry is substituted into the field. The original content and attributes can still be accesed the same:

    for teacher in parallel.teacher:
        teacher() - full name (original field content)
        teacher("xlink:href") - the xlink (original field attribute value)
        teacher.firstName() - value from the fetched xlinked entry

The field type is detected automatically and parsed:
* date to datetinme.date
* datetime to datetime.datetime
* integer to int
* boolean to bool

You can still access the original value by using a kwarg raw=True:

    exam.startDate() # datetime.datetime(2014, 1, 5, 10, O)
    exam.startDate(raw=True) # '2014-01-05T10:00:00'

If you don't understand something, see the examples. Fill in your username (example: buriama8) and password (HPH, the one for KOS) in example.py and get started!

Performance
-----------
kosapy has been developed literally overnight, so it might have preformance issues. It uses lazy loading of xreffed resources and features a simple http cache, but further speedups are sure possible. We'll see if it gets slow enough to be annoying.

MISC
----
kosapy is very young, it might cange drastically in the future, But we still strongly encourage you to use it and report bugs!

We will be implementing OAuth2. Sometime.

Supporting POST, PUT and others is not neccessary for KosAPI, but useful for writeable REST APIs. We might implement them sometime.
