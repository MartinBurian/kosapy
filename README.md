kosapy
======

kosapy is a python client library for KosAPI, a REST API created to access the study information system KOS on CTU Prague.

It is based on the implementation ideas of the [*siesta project*](https://github.com/scastillo/siesta). It is left to the user to take care of calling the API in a valid way as the library has no bindings to the API structure. It could even (after slight modifications) be used for nearly any REST API. The only presumptions made about the XML is organization of data into an ATOM feed and cross-referencing using xlink:href attribute.

    k=Kosapy(url, ('username', 'password'))

Resources
---------
A resource is referenced by k.resource.sub.ssub, e.g.
    k.students.buriama8.enrolledCourses

If the resource is not a valid python identifier, use the get method:
    k.resource.get("invalid:recource-name").ssub

The resource contents are fetched by calling or iterating over the resource:
Fetch one entry:
    entry=k.students.buriama8()

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
In the entry you access the fields in the atom:content tag hierarchically. Accessing the day in parallel entry is
    parallel.timetableSlot.day

If the tag names are not valid python identifiers, use the get() method instead:
    parallel.get("timetableSlot").day
get() supports filtering:
    parallel.get("teacher", rel="stylesheet")
selects all teachers with rel="stylesheet" attribute.

The returned field is always iterable:
    for slot in parallel.timetableSlot:
        print(slot.day)

When there are more tags with the same path (e.g. parallel.teacher), the result is a list; when the tag is only one, it
can be used directly:
parallel.semester.code

The rule of the thumb is: when you are sure there can be only one tag, use it directly. When there is even a slight
possibility that there will be more, iterate. It's guaranteed to work.

Get tag content by calling: parallel.code()
Get tag attribute by calling too: parallel.course("xlink:href)

kosapy deals with xlink references for you, so listing enrolled exam dates is as simple as

    for registration in k.students.buriama8.registeredExams:
        print registration.exam.startDate()

The referenced resource is fetched for you and the resulting entry is substituted into the field. The original content and attributes can still be accesed the same:

    for teacher in parallel.teacher:
        teacher() - full name (original document content)
        teacher("xlink:href") - the xlink (original attribute value)
        teacher.firstName() - value from the fetched entry

If sou don't understand anything, see the examples. Fill in your username (example: buriama8) and password (HPH, the one for KOS) in example.py and get started!

Performance
-----------
kosapy has been developed literally overnight, so it might have preformance issues. It uses lazy loading of xreffed resources and features a simple http cache.

MISC
----
kosapy is very young, it might cange drastically in the future, But we still strongly encourage you to use it and report bugs!

We will be implementing OAuth2. Sometime.

Supporting POST, PUT and others is not neccessary for KosAPI, but useful for writeable REST APIs. We might implement them sometime.