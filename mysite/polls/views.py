import json
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, JsonResponse
from polls.models import Question, Choice
from django.shortcuts import get_object_or_404


def index(request):
    question_list = Question.objects.order_by("-pub_date")[:5].values()
    serialized_list = list(question_list)
    return JsonResponse({"data": serialized_list}, safe=True)


def detail(request, question_id):
    try:
        question = get_object_or_404(Question, pk=question_id)

        if not question:
            raise Http404("Question does not exist!")

        data = [{"success": True, "data": str(question)}]

        return JsonResponse({"data": data})
    except Http404 as e:
        print("error", e)
        return JsonResponse(({"detail": str(e)}), status=404)


def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    print(question.question_text)

    return JsonResponse(
        {
            "success": True,
            "question": question.question_text,
            "results": list(question.choice_set.all().values()),
        }
    )


@csrf_exempt
def vote(request, question_id):
    if request.method == "POST":
        try:
            form_data = request.POST["choice"]
            post_choice_id = int(form_data)

            question = get_object_or_404(Question, pk=question_id)

            available_choice = [choice.id for choice in question.choice_set.all()]

            if post_choice_id not in available_choice:
                raise Http404("Choice does not exist for question!")

            selected_choice = get_object_or_404(Choice, pk=post_choice_id)

            selected_choice.votes += 1
            selected_choice.save()

        except Http404 as e:
            print("error", e)
            return JsonResponse(({"success": False, "detail": str(e)}), status=404)

        except KeyError as e:
            return JsonResponse(
                ({"success": False, "detail": "Value not provided for choice"}),
                status=400,
            )
        except ValueError:
            return JsonResponse(
                (
                    {
                        "success": False,
                        "detail": "Invalid value of '%s' provided for choice"
                        % form_data,
                    }
                ),
                status=400,
            )

        return JsonResponse(
            {"success": True, "message": "You've voted on question %s!" % question_id}
        )
    return JsonResponse(({"detail": "Route does not exist!"}), status=404)
