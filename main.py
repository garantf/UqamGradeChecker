import requests
import os
import sys
import smtplib
import creds
import json
import ssl
from email.message import EmailMessage

# Email that sends notification (https://youtu.be/g_j6ILT-X0k check this video for complete tutorial)
email_sender = creds.email_sender
email_sender_pass = creds.email_sender_pw

# URL of request
request_url1 = 'https://monportail.uqam.ca/authentification'
request_url2 = 'https://monportail.uqam.ca/apis/resumeResultat/identifiant'

payload = {
    'identifiant': creds.identifiant,
    'motDePasse': creds.motDePasse
}

# Send an email Function
def send_email(sigle, note):
    em= EmailMessage()
    em['From'] = creds.email_sender
    em['To'] = creds.email_receiver
    em['Subject'] = 'Tu as reçu une nouvelle note !'
    note = 'N/A' if note is None else note  # Handle null note
    content = 'Clique sur ce lien pour la découvrir: https://monportail.uqam.ca\n\n' + \
               'Sigle: ' + sigle + '\n' + \
               'Note: ' + note
    em.set_content(content)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context ) as smtp:
        smtp.login(creds.email_sender, creds.email_sender_pw)
        smtp.sendmail(creds.email_sender, creds.email_receiver, em.as_string())


#Function that check if you've received a new grade
def checkChanges(new_data):
    # Load the saved data file
    with open('notes.json', "r", encoding='utf-8') as f:
        saved_data_str = f.read()  
        old_data = json.loads(saved_data_str)  # parse the string as JSON

    #Check if the file are the same
    if new_data != old_data:  
        #iterating through all the elements of the first json
        for old_result in old_data['data']['resultats']:
            for old_program in old_result['programmes']:
                for old_activity in old_program['activites']:
                    old_note = old_activity.get('note')
                    old_compteurEvaluation = old_activity.get('compteurEvaluation')
                    for new_result in new_data['data']['resultats']:
                        for new_program in new_result['programmes']:
                            for new_activity in new_program['activites']:
                                new_sigle = new_activity.get('sigle')
                                new_note = new_activity.get('note')
                                new_compteurEvaluation = new_activity.get('compteurEvaluation')
                                # Compare the values
                                if old_note != new_note:
                                    send_email(new_sigle, new_note)
                                    # send_sms()
                                    with open('notes.json', 'w', encoding='utf-8') as f:
                                        json.dump(new_data, f, ensure_ascii=False, indent=2)
                                    sys.exit()
                                if old_compteurEvaluation != new_compteurEvaluation:
                                    send_email(new_sigle, new_note)
                                    # send_sms()
                                    with open('notes.json', 'w', encoding='utf-8') as f:
                                        json.dump(new_data, f, ensure_ascii=False, indent=2)
                                    sys.exit()

        #Check if there's more keys in the new json
        new_keys = set(new_data.keys()) - set(old_data.keys())
        if new_keys:
            send_email()
            # send_sms()
            with open('notes.json', 'w', encoding='utf-8') as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
            sys.exit()

    
# Check if the script has been run before
if not os.path.exists("notes.json"):
    # Headers for the first request to obtain our JWT
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://monportail.uqam.ca',
    'Referer': 'https://monportail.uqam.ca/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

    # Creating a session object
    session = requests.Session()

    # Json Object containing our JWT token
    response_Jwt_Token = session.post(request_url1, headers=headers, json=payload)
    response_data = response_Jwt_Token.json()

    # Extracting our token and creating cookies object
    token = response_data["token"]
    cookiez = '%22'+token+'%22'
    cookies = {
        'token': cookiez,
    }

    # Second headers for our second request to obtain a json with all our grades in it
    headers2 = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Authorization': 'Bearer '+ token,
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'If-Modified-Since': '0',
    'Referer': 'https://monportail.uqam.ca/resultats/20241',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

    response = session.get(request_url2, cookies=cookies, headers=headers2)

    # Convert the response to a JSON object
    data = json.loads(response.text)

    with open('notes.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Compare the current webpage with the saved version
else:

  # Headers for the first request to obtain our JWT
    headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://monportail.uqam.ca',
    'Referer': 'https://monportail.uqam.ca/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

    # Creating a session object
    session = requests.Session()

    # Json Object containing our JWT token
    response_Jwt_Token = session.post(request_url1, headers=headers, json=payload) 
    response_data = response_Jwt_Token.json()

    # Extracting our token and creating cookies object
    token = response_data["token"]
    cookiez = '%22'+token+'%22'
    cookies = {
        'token': cookiez,
    }

    # Second headers for our second request to obtain a json with all our grades in it
    headers2 = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Authorization': 'Bearer '+ token,
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'If-Modified-Since': '0',
    'Referer': 'https://monportail.uqam.ca/resultats/20241',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
}

    response = session.get(request_url2, cookies=cookies, headers=headers2)

    # Convert the response to a JSON object
    data = json.loads(response.text)
    checkChanges(data)
