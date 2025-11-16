from django.shortcuts import render

def global_map(request):
    return render(request, "monitoring/global_map.html")

