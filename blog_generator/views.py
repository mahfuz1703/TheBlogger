from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from pytube import YouTube
import assemblyai as aai
import os
from django.conf import settings
import openai

# Create your views here.
@login_required
def home(request):
    return render(request, "index.html")

def signin(request):
    if  request.method == "POST":
        username = request.POST['login_username']
        password = request.POST['login_password']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect(reverse('admin:index'))
            else:
                return render(request, "index.html", {'username': username})
        else:
            error_message2 = "User not found. Please try again!!!"
            return render(request, "login.html", {'error_messag2': error_message2})
    return render(request, "login.html")

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            error_message = "Password does not match!!"
            return render(request, "signup.html", {'error_message': error_message})
        elif User.objects.filter(username=username).exists():
            error_message = "Username already exists!!"
            return render(request, "signup.html", {'error_message': error_message})
        elif User.objects.filter(email=email).exists():
            error_message = "Email already uses!!"
            return render(request, "signup.html", {'error_message': error_message})
        else:
            try:
                user = User.objects.create_user(username=username, email=email, password=pass1)
                user.save()
                return redirect(signin)
            except:
                error_message = "Error creating account!!"
                return render(request, "signup.html", {'error_message': error_message})
    return render(request, "signup.html")


def all_saved_blog(request):
    return render(request, "all_blogs.html")

def blog_details(request):
    return render(request, "blog_details.html")

def signout(request):
    logout(request)
    return redirect(home)


@csrf_exempt
def generate_blog(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)


        # get yt title
        title = yt_title(yt_link)

        # get transcript
        transcription = get_transcription(yt_link)
        if not transcription:
            return JsonResponse({'error': " Failed to get transcript"}, status=500)


        # use OpenAI to generate the blog
        blog_content = generate_blog_from_transcription(transcription)
        if not blog_content:
            return JsonResponse({'error': " Failed to generate blog article"}, status=500)

        # save blog article to database
        # new_blog_article = BlogPost.objects.create(
        #     user=request.user,
        #     youtube_title=title,
        #     youtube_link=yt_link,
        #     generated_content=blog_content,
        # )
        # new_blog_article.save()

        # return blog article as a response
        return JsonResponse({'content': blog_content})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    yt = YouTube(link)
    title = yt.title
    return title

def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

def get_transcription(link):
    audio_file = download_audio(link)
    aai.settings.api_key = "d706d9145fe344de8db8be3340546598"

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    return transcript.text

def generate_blog_from_transcription(transcription):
    openai.api_key = "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"

    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{transcription}\n\nArticle:"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )

    generated_content = response.choices[0].text.strip()

    return generated_content

