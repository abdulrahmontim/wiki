from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django import forms
from markdown2 import markdown
from random import choice

from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(label="Enter Title")
    text = forms.CharField(widget=forms.Textarea(), label="")
    
class EditPageForm(forms.Form):
    text_field = forms.CharField(widget=forms.Textarea(), label="")
        

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    if md_content := util.get_entry(title):
        html_content = markdown(md_content)
        
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": html_content
        })
         
    else:
        return render(request, "encyclopedia/error.html", {
            "error_message": "Entry doesn't exist.",
            "error_code": "404",
            "error_text": "Page Not Found."
        })

def new(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            text = form.cleaned_data["text"]
            
            for entry in util.list_entries():
                if title.lower() == entry.lower():
                    return render(request, "encyclopedia/error.html", {
                        "error_message": "Entry already exist.",
                        "error_code": "",
                        "error_text": "Entry Error"
                    })
                    
            else:
                util.save_entry(title, text)
                return HttpResponseRedirect(reverse('entry', args=[title]))
            
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
        
    return render(request, "encyclopedia/new.html", {
        "form": NewPageForm(),
    })
    
def random(request):
    random_page = choice(util.list_entries())
    return HttpResponseRedirect(reverse('entry', args=[random_page]))

def edit(request, title):
    md_content = util.get_entry(title)
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text_field"]
            if title in util.list_entries():
                util.save_entry(title, text)
                return HttpResponseRedirect(reverse('entry', args=[title]))
            else:
                return render(request, "encyclopedia/error.html", {
                    "error_text": "Entry doesn't exist.",
                    "error_code": "404",
                    "error_message": "Seems the page requested has been deleted or doesn't exist."
                })
        
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form,
            })

    return render(request, "encyclopedia/edit.html", {
        "form": EditPageForm(initial={'text_field': md_content}),
        "title": title,
    })

def search(request):
    query = request.GET.get('q').strip()
    query_result = []
    
    for entry in util.list_entries():
        
        if query.lower() == entry.lower():
            return HttpResponseRedirect(reverse('entry', args=[entry]))
        
        elif query.lower() in entry.lower():
            query_result.append(entry)

    else:
        return render(request, "encyclopedia/search.html", {
            "query_result": query_result,
            "query": query,
        })