__author__ = 'martinjr'

from __init__ import Kosapy

if __name__=="__main__":
    k=Kosapy("https://kosapi.feld.cvut.cz/api/3b/", ("buriama8", "A02T3Dcvut"))
    studs=k.students # students resource
    exams=k.exams # exams resource

    # single student information
    s=studs.buriama8() # fetch student buriama8
    print("%s %s"%(s.firstName(), s.lastName()))
    print(s.faculty.code()) # xlinked faculty

    # dates and courses of registered exams
    for e in studs.buriama8.registeredExams:
        print(e.exam.startDate().strftime("%d/%m/%Y"), e.exam.course())

    # dates of OPT exams
    for e in exams(query="course==A4B33OPT", sem="B131"):
        print(e.startDate().strftime("%d/%m/%Y %H:%M"))

    # student's parallels in semester B122
    for p in studs.buriama8.parallels(sem="B122"):
        print("%s (%s) - %d"%(p.course(), p.course.code(), p.code())) # code from xlinked entry

    # all Martins currently on FEE
    # larger limit means less paging
    # This'll take quite some time, kill me when you get bored.

    for s in studs(query="firstName==Martin", limit=100):
        print("%s %s"%(s.firstName(), s.lastName()))

    # Try rerunning me and see the cache at work!