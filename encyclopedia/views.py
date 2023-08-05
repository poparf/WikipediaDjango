from django.shortcuts import render
from markdown2 import Markdown
from . import util
from django.http import Http404,HttpResponse, HttpResponseRedirect, HttpRequest
from django.urls import reverse
from django import forms
import random
import datetime

class CreateArticle(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"rows":"5", "style" :"width:400px;"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":"5","style": "height:400px; width:400px"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):

    entries = util.list_entries()

    for entry in entries:
        if title.lower() == entry.lower():
             # Converts from markdown to plain html and uses |safe in entry.html !
            markdowner = Markdown()
            return render(request, "encyclopedia/entry.html", {
                "title":title,
                "entry":markdowner.convert(util.get_entry(title))
            })
    raise Http404("Page not found.")


def handle_404(request,exception):
    
    return render(request, 'encyclopedia/404.html', {
        "status":404,
        "url": request.build_absolute_uri()
    })




def search(request):
    if request.method == 'GET' and 'q' in request.GET:
        title = request.GET['q']
        if title != '':
           # check if something similar to tile searched is present
           entries = util.list_entries()
           found_entries = []
           
           for entry in entries:
               if title.lower() in entry.lower():
                   found_entries.append(entry)
        
           if found_entries != []:
               return render(request, 'encyclopedia/search.html', {
                   'entries': found_entries,
                   'search_key': title
               })
           return render(request, 'encyclopedia/index.html', {
               'search_error': True,
               "entries": util.list_entries(),
               "search_key": title
           })
        

    # this part is executed if there is no ?q= parameter and if it is present with nothing inside
    return HttpResponseRedirect(reverse('index'))



def create(request):

    if request.method == 'POST':
        article_html = CreateArticle(request.POST)
        
        if article_html.is_valid():
            article_title = article_html.cleaned_data['title']
            article_title_lower = article_title.lower()
            entries = util.list_entries()
            entries.sort(key=lambda x: x.lower())  # Sort case-insensitively
            entries = [x.lower() for x in entries]

            # Binary search
            i = 0
            j = len(entries) - 1  # Corrected to adjust for 0-based indexing
            found = False  # Use boolean for clarity

            while i <= j and not found:
                mid = i + (j - i) // 2  # Use integer division
                mid_entry = entries[mid].lower()  # Convert to lowercase for comparison

                if mid_entry == article_title_lower:
                    found = True
                elif mid_entry < article_title_lower:
                    i = mid + 1
                else:
                    j = mid - 1
            
            if(found):
                # there is already an article with that title
                return render(request, 'encyclopedia/create.html', {
                    "createArticleForm": CreateArticle(),
                    "message": 1,
                    "title": article_title
                })
            
            article_content = article_html.cleaned_data['content']

            util.save_entry(article_title, article_content, None)

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'encyclopedia/create.html', {
        "createArticleForm": CreateArticle()
    })



def edit(request,title):

    initial_article_content = util.get_entry(title)

    if request.method == "POST":
        article_html = CreateArticle(request.POST)

        if article_html.is_valid():
            # verify if the edited title already exists among other articles
            edited_article_title = article_html.cleaned_data['title']
            edited_article_content = article_html.cleaned_data['content']

            # wrong behaviour: if the title is changed in another existing article title besides the one edited, the other one gets the name changed
            # wantted behaviour: we want to show an error
            # all entries sorted
            entries = util.list_entries()
            lowerTitle = title.lower()
            edited_article_title_lower = edited_article_title.lower()
            entries.sort(key=lambda x: x.lower())
            entries = [x.lower() for x in entries]
            entries.pop(entries.index(lowerTitle))

            for entry in entries:
                if entry == edited_article_title_lower:
                    return render(request, 'encyclopedia/edit.html', {
                        'title':title,
                        'form': CreateArticle(initial={'title':title, 'content':edited_article_content}),
                        "edited_article_title": edited_article_title,
                        "message": 1
                    })
                    

            if edited_article_title.lower() is title.lower():
                util.save_entry(edited_article_title, edited_article_content, None)
            else:
                util.save_entry(edited_article_title,edited_article_content, title)
            
            return HttpResponseRedirect(reverse('entry', args=[edited_article_title]))

    return render(request, 'encyclopedia/edit.html', {
        'title':title,
        'form': CreateArticle(initial={'title':title, 'content':initial_article_content})
    })


def random_view(request):
    
    # we use the time seed so we can assure that we will have a different result everytime.
    now = datetime.datetime.now()
    seed = int(now.timestamp())
    random.seed(seed)

    entries = util.list_entries()

    random_entry = random.choice(entries)
    print(random_entry)
    
    return HttpResponseRedirect(reverse('entry', args=[random_entry]))