from . import models
from django.shortcuts import render, redirect
from django.http import *
from django.core.exceptions import *
from django.utils import timezone
from django.db.models import Value, CharField, FloatField
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
# Create your views here.
def is_ta_or_superuser(user):
    return is_ta(user) or is_superuser(user)

def is_student(user):
    return user.groups.filter(name="Students").exists()

def is_ta(user):
    return user.groups.filter(name="Teaching Assistants").exists()

def is_superuser(user):
    return user.is_superuser

def pick_grader(assignment):
    return models.Group.objects.get(name="Teaching Assistants").user_set.annotate(total_assigned=Count("graded_set", filter=Q(graded_set__assignment=assignment))).order_by("total_assigned").first()

@login_required
def assignments(request):
    assignments = models.Assignment.objects.order_by("deadline")
    return render(request, "assignments.html", dict(assignments=assignments))

@login_required
def index(request, assignment_id):
    try:
        status = ""
        numStudents = models.Group.objects.get(name="Students").user_set.count()
        assignment = models.Assignment.objects.get(id = assignment_id)
        mySubmissions = models.Submission.objects.filter(grader_id = request.user.id).filter(assignment = assignment).count()
        submission = models.Submission.objects.filter(author_id=request.user.id).filter(assignment = assignment).first()
        if(is_student(request.user)):
            if (assignment.deadline < timezone.now()):
                if(assignment.submission_set.all().filter(author_id = request.user.id).count() == 0):
                    status = "missing"
                elif(assignment.submission_set.all().filter(author_id = request.user.id).exclude(score = None).count() != 0):
                    status = "graded"
                else:
                    status = "ungraded"
            else:
                if(assignment.submission_set.all().filter(author_id = request.user.id).count() == 0):
                    status = "notsubmitted"
                else:
                    status = "submitted"

        context = {
            'assignment': assignment,
            'totalsubmissions': assignment.submission_set.all().count(),
            'mysubmissions': mySubmissions,
            'students': numStudents,
            'user': request.user,
            'is_ta': not is_student(request.user),
            'status': status,
            'submission': submission,
        }
        return render(request, 'index.html', context)
    
    except models.Assignment.DoesNotExist:
        raise Http404("assignment does not exist")

@login_required
@user_passes_test(is_ta_or_superuser)
def submissions(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id = assignment_id)
        if(is_ta(request.user)):
            submissions = assignment.submission_set.all().filter(grader_id = request.user.id).order_by('author')
        if(is_superuser(request.user)):
            submissions = assignment.submission_set.all().order_by('author')
        context = {
            "assignment": assignment,
            "submissions": submissions
        }
        return render(request, "submissions.html", context)
    except:
        raise Http404("assignment does not exist")

@login_required
def profile(request):
    assignments = models.Assignment.objects.order_by("deadline")
    assignments.annotate(status=Value("Not Due", output_field=CharField()))
    mySubmissions = []
    gradedSubmissions = []
    totalPoints = 0
    studentsPoints = 0
    for assignment in assignments:
        if(is_ta(request.user)):
            mySubmissions = assignment.submission_set.all().filter(grader_id = request.user.id).count()
            gradedSubmissions = assignment.submission_set.all().filter(grader_id = request.user.id).exclude(score = None).count()
            if assignment.deadline < timezone.now():
                assignment.status = str(gradedSubmissions) + "/" + str(mySubmissions)
            else:
                assignment.status = "Not Due"
        if(is_superuser(request.user)):
            mySubmissions = assignment.submission_set.all().count()
            gradedSubmissions = assignment.submission_set.all().exclude(score = None).count()
            if assignment.deadline < timezone.now():
                assignment.status = str(gradedSubmissions) + "/" + str(mySubmissions)
            else:
                assignment.status = "Not Due"
        if(is_student(request.user)):
            if (assignment.deadline < timezone.now() and assignment.submission_set.all().filter(author_id = request.user.id).count() == 0):
                totalPoints += assignment.weight
                assignment.status = "Missing"
            elif(assignment.deadline < timezone.now() and assignment.submission_set.all().filter(author_id = request.user.id).exclude(score = None).count() == 0):
                assignment.status = "Ungraded"
            elif(assignment.deadline > timezone.now()):
                assignment.status = "Not Due"
            else:
                totalPoints += assignment.weight
                score = assignment.submission_set.all().filter(author_id = request.user.id).first().score
                points = assignment.points
                assignment.status = str(score / points * 100) + "%"
                studentsPoints += score / points * assignment.weight

        if(totalPoints == 0):
            totalGrade = 100
        else:
            totalGrade = studentsPoints / totalPoints * 100
    context = {
        'assignments': assignments,
        'mysubmissions': mySubmissions,
        'gradedsubmissions': gradedSubmissions,
        'user': request.user,
        'totalgrade': totalGrade,
        'is_student': is_student(request.user),
    }
    return render(request, 'profile.html', context)

def login_form(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        next = request.POST.get("next", "/profile/")
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect(next)
        else:
            context = {
            'next': next,
            'error': "Username and password do not match"
        }
            return render(request, 'login.html', context)
    else:
        context = {
            'next': request.GET.get("next", "/profile/"),
        }
        return render(request, 'login.html', context)

@login_required
@user_passes_test(is_ta_or_superuser)
def grade(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id = assignment_id)
    except:
        raise Http404("assignment does not exist")
    for key, value in request.POST.items():
        if(key.startswith('grade-')):
            sub_id = int(key.split('-')[1])
            try:
                submission = models.Submission.objects.get(id = sub_id)
            except:
                raise Http404("submission does not exist")
            try:
                if(float(value) < 0 or float(value) > assignment.points):
                    raise ValueError()
                submission.score = float(value)
                submission.save()
            except ValueError:
                submission.score = None
                submission.save()
            
    return redirect(f"/{assignment_id}/submissions")

def logout_form(request):
    logout(request)
    return redirect("/profile/login")

@login_required
@user_passes_test(is_student)
def submit(request, assignment_id):
    try:
        assignment = models.Assignment.objects.get(id = assignment_id)
    except:
        raise Http404("assignment does not exist")
    if (assignment.deadline < timezone.now()):
        raise Http404("Past Due")
    file = request.FILES.get("file", "")
    if(models.Submission.objects.filter(author_id=request.user.id).filter(assignment = assignment).count() == 0):
        grader = pick_grader(assignment)
        submission = models.Submission(assignment=assignment, author=request.user, grader=grader, file=file, score=None)
        submission.save()
    else:
        submission = models.Submission.objects.filter(author_id=request.user.id).filter(assignment = assignment).first()
        submission.file = file
        submission.save()
    
    return redirect("/%s/" % assignment_id)

@login_required
def show_upload(request, filename):
    submission = models.Submission.objects.get(file=filename)
    if(request.user == submission.author or request.user == submission.grader or is_superuser(request.user)):
        with submission.file.open() as fd:
            response = HttpResponse(fd)
            response["Content-Disposition"] = \
                f'attachment; filename="{submission.file.name}"'
            return response
    else:
        raise PermissionDenied("Invalid user")




