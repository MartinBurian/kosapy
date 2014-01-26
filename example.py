__author__ = 'martinjr'

from __init__ import Kosapy

if __name__=="__main__":
    k=Kosapy("https://kosapi.feld.cvut.cz/api/3b/", ("USER", "PASSWD"))
    studs=k.students
    exams=k.exams

    # fetch student
    s=studs.buriama8()
    print("%s %s"%(s.firstName(), s.lastName()))
    # xlinked faculty
    print(s.faculty.code())

    # dates and courses of registered exams
    for e in studs.buriama8.registeredExams:
        print(e.exam.startDate().strftime("%d/%m/%Y"), e.exam.course())

    # dates of OPT exams
    for e in exams(query="course==A4B33OPT"):
        print(e.startDate().strftime("%d/%m/%Y %H:%M"))

    # parallels in semester B122
    for p in studs.buriama8.parallels(sem="B1š22"):
        print(p.course()) # original tag content
        print(p.course.code()) # code from xlinked entry

    # all Martins currently on FEE
    # larger limit means less paging
    # This'll take quite some time, kill me when you get bored.

    for s in studs(query="firstName==Martin", limit=100):
        print("%s %s"%(s.firstName(), s.lastName()))

    # Try rerunning me and see the cache at work!