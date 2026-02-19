from django.shortcuts import render
from .models import Questions , Choice
from django.template import loader
from django.http import Http404
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

# def index(request):
#     latest_question_list = Questions.objects.order_by("-pub_date")[:5]
#     template = loader.get_template("polls/index.html")
#     context = {"latest_question_list": latest_question_list}
#     # output = ", ".join([q.question_text for q in latest_question_list])
#     # return HttpResponse(output)
#     return HttpResponse(template.render(context, request))


# def index(request):
#     latest_question_list = Questions    .objects.order_by("-pub_date")[:5]
#     context = {"latest_question_list": latest_question_list}
#     return render(request, "polls/index.html", context)

# def detail(request , question_id):
#     return HttpResponse("You're looking at question %s." % question_id)

# def detail(request, question_id):
#     question = get_object_or_404(Questions, pk=question_id)
#     return render(request, "polls/detail.html", {"question": question})

# def detail(request, question_id): 
#     try:
#         question = Questions.objects.get(pk=question_id)
#     except Questions.DoesNotExist:
#         raise Http404("Question does not exist")
#     return render(request, "polls/detail.html", {"question": question})

# def results(request , question_id):
#     response = "you're looking at the results of question %s."
#     return HttpResponse(response % question_id)

# def results(request, question_id):
#     question = get_object_or_404(Questions, pk=question_id)
#     return render(request, "polls/results.html", {"question": question})

# def vote(request , question_id):
#     return HttpResponse("you're voting on question %s." % question_id)


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    # def get_queryset(self):
    #     """Return the last five published questions."""
    #     return Questions.objects.order_by("-pub_date")[:5]

    def get_queryset(self):
        # `   """ Return the last five published questions (not including those set to be published in the future)."""
        return  Questions.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[ :5]


class DetailView(generic.DetailView):
    model = Questions
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Questions.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Questions   
    template_name = "polls/results.html"
    context_object_name = "question"



def vote(request, question_id):
    question = get_object_or_404(Questions, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))