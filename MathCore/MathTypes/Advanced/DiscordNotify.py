import urllib.request
import json
import ssl
import unreal 

def send_to_discord(status):
    # --- 1. CONFIGURATION ---
    # Paste your actual URL inside the quotes below
    webhook_url = "https://discordapp.com/api/webhooks/1452019900657827925/lTVhjolcp9MgomIZ9HXz_Yfe2eR2iipHON9B9GULnaTHaXouDuz2tk9EaO9We7VyUB2O"
    user = "alviespurlock"
    
    # --- 2. AUTOMATIC PROJECT DETECTION ---
    # This grabs the name of your .uproject file automatically
    project_name = unreal.Paths.get_base_filename(unreal.Paths.get_project_file_path())
    
    # Fallback if the name is empty for some reason
    if not project_name:
        project_name = "Unknown Project"

    # --- 3. BUILD PAYLOAD ---
    payload = {
        "username": "Unreal Engine AI Bot",
        "content": f"**{user}** {status} Unreal Engine\n**Project:** {project_name}"
    }
    
    # --- 4. SEND REQUEST ---
    if "your_actual_link_here" in webhook_url:
        unreal.log_error("ScrapBot: You forgot to paste your Webhook URL into the script!")
        return

    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    req = urllib.request.Request(webhook_url, data=data, headers=headers, method='POST')
    context = ssl._create_unverified_context()
    
    try:
        unreal.log(f"ScrapBot: Sending Discord update for {status}...")
        with urllib.request.urlopen(req, context=context) as res:
            if res.getcode() in [200, 204]:
                unreal.log(f"ScrapBot: {project_name} notification sent successfully!")
    except Exception as e:
        unreal.log_error(f"ScrapBot: Failed to send notification. Error: {e}")

# Trigger the "Open" message
send_to_discord("Has opened")