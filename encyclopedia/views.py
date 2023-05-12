from django.shortcuts import render, HttpResponseRedirect
from django import forms
from django.urls import reverse
from random import choice
import markdown2

from . import util

class NewPageForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput())
    body = forms.CharField(widget=forms.Textarea(attrs={'style': "width:100%;"}))

def index(request):
    # POST METHOD
    if request.method == "POST":
        # If there is the entry/blog, the user is redirected to the entry page (request.POST['q'] - taking the data from POST method)
        if util.get_entry(request.POST['q']):
            return render(request, "encyclopedia/entry.html", {
            "entries": markdown2.markdown(util.get_entry(title=request.POST['q'])),
            "title": request.POST['q']
            })
        # If the user's input does not match with any of the entry name:
        else:
            # Searching for substring in the all entries
            sub_list=[]
            for entry in util.list_entries():
                if request.POST['q'] in entry or request.POST['q'].capitalize() in entry or request.POST['q'].upper() in entry:
                    sub_list.append(entry)
            # If there is any matching, the search-result page will display the matching results
            if sub_list:
                return render(request, "encyclopedia/search-result.html", {
                "entries": sub_list
                })
            # But if there is no any matching, display the list of all entries
            else:
                return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries()
                })
    # GET METHOD
    else:
        return render(request, "encyclopedia/index.html", {
                    "entries": util.list_entries()
                })

def entry(request, title):
    # Taking the <str:title> (Check the encyclopedia/urls.py) from the URL(GET method) and displaying the entry if there is:
    if util.get_entry(title=title):
        # Rendering the entry page with markdown content and in HTML I used {{ entries|safe }}, and passing the title
        return render(request, "encyclopedia/entry.html", {
            "entries": markdown2.markdown(util.get_entry(title=title)),
            "title": title
        })
    # If the page is not found, display the error.html
    else:
        return render(request, "encyclopedia/error.html")

def create(request):
    # POST
    if request.method == "POST":
        # Taking the DATA from POST
        page = NewPageForm(request.POST)
        # Checking is the DATA valid
        if page.is_valid():
            # Checking is there page with same title, if there is the error will be displayed
            if util.get_entry(page.cleaned_data["title"]):
                error = True
                return render(request, "encyclopedia/create.html", {
                "form": NewPageForm(request.POST),
                "error": error,
                })
            # If the page is new:
            else:
                # Taking DATA(title, body)
                title = page.cleaned_data["title"]
                body = page.cleaned_data["body"]
                # Creating new file {title}.md
                f = open(f"entries/{title}.md", "w")
                f.write(f"# {title}\n\n")
                f.write(f"{body}")
                f.close()
                # After creating new page, the user is redirected to that new page
                return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
    # GET
    else:
        return render(request, "encyclopedia/create.html", {
            "form": NewPageForm()
        })

def edit(request, title):
    global edited_title 
    edited_title = title
    # POST
    if request.method == "POST":
        # Taking the POST data
        page = NewPageForm(request.POST)
        # Checking is it valid or not
        if page.is_valid():
            # Edited title 
            new_title = page.cleaned_data["title"].capitalize()

            # This is the way without the function from the util.py
            # body = page.cleaned_data["body"]
            # f = open(f"entries/{new_title}.md", "w")
            # f.write(f"/# {new_title}\n\n")
            # f.write(f"{body}")
            # f.close()

            # Using the function from the util.py to save entry
            util.save_entry(new_title)

            # Redirecting the user after editing the entry
            return HttpResponseRedirect(reverse("entry", kwargs={"title": new_title}))
    # GET
    else:
        # After clicking on the EDIT link, the user is redirected to the edit page

        # Here I read the file with title(<str:title>)
        f = open(f"entries/{title}.md")

        # Then from the file, I create list which I will use to pass inital values in class
        lines = f.readlines()
        
        # Here is deleting the file but I will not use this, it is not defined in the tasks
        # util.delete_entry(f"entries/{edited_title}.md")

        # New class with INITIAL values
        class EditPageForm(forms.Form):
            title = forms.CharField(widget=forms.TextInput(), initial=edited_title)
            body = forms.CharField(widget=forms.Textarea(), initial=lines[2])
        # Rendering the class with INITIAL VALUES
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "form": EditPageForm()
        })

def random(request):
    # Getting all list of entries
    list = util.list_entries()
    # Random choice
    random_entry = choice(list)
    # Rendering the random entry
    return render(request, "encyclopedia/entry.html", {
            "entries": markdown2.markdown(util.get_entry(title=random_entry)),
            "title": random_entry
        })

# Additional deleteing the page
def delete_post(request, title):
    # Calling the function
    util.delete_entry(title=title)
    # Rendering the page
    return render(request,  "encyclopedia/index.html", {
        "entries": util.list_entries()
    })