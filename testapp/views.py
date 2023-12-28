import os
from django.shortcuts import render
from django.http import HttpResponse
import speech_recognition as sr
from .models import Assessment

def transcribe_audio(audio_path, accent_name):
    recognizer = sr.Recognizer()

    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)

    try:
        transcribed_text = recognizer.recognize_google(audio, language="en-IN")
        print(f"Transcription successful: {transcribed_text}")
        return transcribed_text
    except sr.UnknownValueError:
        print(f"Google Web Speech API could not understand the {accent_name} audio")
        return None  # Return None in case of transcription failure
    except sr.RequestError as e:
        print(f"Could not request results from Google Web Speech API; {e}")
        return None  # Return None in case of transcription failure
    except Exception as e:
        print(f"An unexpected error occurred during transcription: {e}")
        return None  # Return None in case of transcription failure

def assess_suitability(indian_audio_path):
    indian_text = transcribe_audio(indian_audio_path, "Indian")

    if indian_text is not None:  # Check for transcription success
        
        customer_care_keywords = ["customer service", "support", "assistance", "problem resolution"]
        contains_keywords = any(keyword in indian_text.lower() for keyword in customer_care_keywords)

        result = "The Indian accent is suitable for American customer care." if contains_keywords else "The Indian accent may not be suitable for American customer care."
        assessment = Assessment(audio_file=indian_audio_path, transcription=indian_text, suitability_result=result)
        assessment.save()

        if contains_keywords:
            return "The Indian accent is suitable for American customer care."
        else:
            return "The Indian accent may not be suitable for American customer care."
        
    else:
        return "Transcription failed for the Indian accent."


def hello(request):
    result = None
    if request.method == 'POST':
        audio_file = request.FILES.get('audio_file')

        # Save the uploaded file to a temporary location
        temp_audio_path = os.path.join('temp', audio_file.name)
        with open(temp_audio_path, 'wb') as temp_file:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)

        # Assess the suitability of the uploaded audio
        result = assess_suitability(temp_audio_path)

        # Return the assessment result directly
        return HttpResponse(result)

    return render(request, 'upload.html', {'result': result})