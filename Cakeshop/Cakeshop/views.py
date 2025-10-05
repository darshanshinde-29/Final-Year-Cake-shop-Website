from django.shortcuts import render, HttpResponse, redirect

brand = "CakeZone"

def landing(req):
    if req.user.is_authenticated:
        return redirect('/app/home')
    else:
        return render(req, "landing.html", {'brand':brand})

