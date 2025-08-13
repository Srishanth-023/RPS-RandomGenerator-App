from django.shortcuts import render

# Create your views here.

import json
import random
import cv2
import base64
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# --- Constants ---
# Fine-tuned confidence to be more lenient with finger detection
detector = HandDetector(maxHands=1, detectionCon=0.75)

# --- HELPER FUNCTIONS ---

def _get_move_from_image(img):
    """Analyzes an image to detect a hand gesture for Rock, Paper, or Scissors."""
    hands, _ = detector.findHands(img, draw=False)
    if hands:
        fingers = detector.fingersUp(hands[0])
        
        # Rock: All fingers down
        if fingers == [0, 0, 0, 0, 0]:
            return "rock"
        
        # Paper: All fingers up
        if fingers == [1, 1, 1, 1, 1]:
            return "paper"
        
        # Scissors: Index and middle fingers up (flexible to thumb position)
        if fingers == [0, 1, 1, 0, 0] or fingers == [1, 1, 1, 0, 0]:
            return "scissors"
            
    # If no valid gesture is found, return None
    return None

def _decode_image_from_base64(image_data_string):
    """Decodes a base64 image string from the frontend into an OpenCV image."""
    try:
        image_data = image_data_string.split(',')[1]
        decoded_image = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded_image, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except (IndexError, base64.binascii.Error):
        return None

def get_winner(player_move, ai_move):
    """Determines the winner of the round."""
    if player_move == ai_move:
        return 'tie'
    
    winning_combos = {'rock': 'scissors', 'paper': 'rock', 'scissors': 'paper'}
    
    if winning_combos.get(player_move) == ai_move:
        return 'player'
        
    return 'ai'

# --- DJANGO VIEWS ---

def home_view(request):
    """Renders the initial page where the user enters their name."""
    return render(request, 'game/home.html')

def start_game_view(request):
    """Handles the username form submission and redirects to the main game page."""
    if request.method == 'POST':
        username = request.POST.get('username')
        if username:
            return redirect('game_page', username=username)
    return redirect('home')

def index(request, username):
    """Renders the main game page."""
    context = {'username': username}
    return render(request, 'game/index.html', context)

@csrf_exempt
def analyze_frame(request):
    """
    Receives an image frame from the frontend, determines the player's move,
    gets a random AI move, and returns the round result.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    data = json.loads(request.body)
    img = _decode_image_from_base64(data.get('image', ''))

    if img is None:
        return JsonResponse({'error': 'Invalid image data'}, status=400)

    player_move_str = _get_move_from_image(img)

    if not player_move_str:
        return JsonResponse({'error': 'No hand detected or invalid gesture.'})

    # --- SIMPLIFIED AI LOGIC ---
    # The AI simply chooses a move at random.
    ai_move_str = random.choice(['rock', 'paper', 'scissors'])
    
    winner = get_winner(player_move_str, ai_move_str)

    return JsonResponse({
        'player_move': player_move_str,
        'ai_move': ai_move_str,
        'winner': winner,
    })