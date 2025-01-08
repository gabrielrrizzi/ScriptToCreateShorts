import requests
import json
import text_speech_en
import http.client
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from moviepy.editor import vfx, VideoFileClip, concatenate_videoclips,AudioFileClip
from PIL import Image
import subtitle_video
import upload_video
import tts_google_cloud

def create_content(input): 
    url = "http://localhost:11434/api/chat"

    payload = json.dumps({
    "model": "llama3",

    "messages": [
        {
        "role": "system",
        "content": "Você é um criador de conteúdo excepcional. Gere conteúdo completo e envolvente em português contando uma história ou fato interessante para seu público baseado na palavra-chave fornecida pelo usuário. Sempre inclua uma fala de exatamente um minuto que conte sobre a curiosidade com começo, meio e fim. Não use contrações ou acentuações, e siga esta estrutura: *Fala:* conteúdo da fala / *Titulo:* Titulo chamativo e apelativo / *Descrição:* descrição detalhada sobre o conteúdo e que tenha apelo para o público se inscrever no canal / *Palavra-chave relacionada:* conteúdo da palavra-chave relacionada / *Hashtags relevantes:* conteúdo dos hashtags relevantes. No final da fala, lembre o público de se inscrever no canal."
        },
        
        {
        "role": "user",
        "content": input
        }
    ],
    "stream": False
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)    

    response_dict = json.loads(response.content)

    message = response_dict.get("message")

    json_response = message.get("content")

    list_json = json_response.split("*")

    print("Conteudo Escrito Criado")

    return list_json

def create_sound(text,keyword):
    text = text.replace("\n"," ").replace("\\"," ").replace('"'," ").replace("'","")
    duration = tts_google_cloud.ttsCloudGoogle(text)
    print("Audio Criado")
    return duration

def search_video(keyword,duration):
    conn = http.client.HTTPSConnection("api.pexels.com")
    payload = ''
    headers = {
    'Authorization': 'Seu Token de autorização',
    'Cookie': ''
    }
    conn.request("GET", "/videos/search?query="+ keyword.replace(" ","%20").replace('"',"").replace("\n","") + "&per_page=15&orientation=portrait", payload, headers)
    response = conn.getresponse()
    data = response.read()
    response_dict = json.loads(data)
    videos = response_dict.get("videos")
    videos_quantity = calculate_how_many_video(videos=videos,duration=duration)
    files = download_video(videos,videos_quantity)
    return files 

def download_video(videos,videos_quantity):   
    files = [] 
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
    "download.default_directory": "/path/to/download/directory",  # Definir o diretório de download
    "download.prompt_for_download": False,  # Desabilitar prompt de download
    "download.directory_upgrade": True,  # Permitir a atualização do diretório de download
    "safebrowsing.enabled": True  # Desabilitar segurança do navegador para baixar
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    for i in range(videos_quantity):       
       videos_file = videos[i]['video_files']
       video_file_hd = [video for video in videos_file if video['file_type'] == 'video/mp4']
       url = video_file_hd[0]['link']   

       driver.get(url)

       parsed_url = urlparse(url)
       file_name = parsed_url.path.split('/')[-1]
       
       files.append(file_name)

       time.sleep(20)

    driver.quit()

    return files

def calculate_how_many_video(videos,duration):
    counter = 0

    for item in videos:                 
        if duration <= 0:
            break 
        duration = duration - videos[counter]["duration"]
        counter = counter + 1

    return counter   

def compile_video(files,keyword):
    clips = []
    target_resolution = (1080,1920)
    for file in files:
        video = VideoFileClip("C:\\Users\\Pichau\\Downloads\\" + file).without_audio()
        resized_video = video.resize(target_resolution, Image.Resampling.LANCZOS)
        clips.append(resized_video)

    video = concatenate_videoclips(clips)    
    audio = AudioFileClip("D:\\Python\\Python_Automation\\Automation_Video_Script\\output.wav")
    video = video.subclip(0, audio.duration)
    video_with_audio = video.set_audio(audio)

    video_with_audio.write_videofile(keyword + ".mp4", codec="libx264",audio_codec= "aac")  

def main(): 

    with open('palavras.txt', 'r', encoding='utf-8') as file:
        
        linhas = file.readlines()

    for linha in linhas:
        linha = linha.strip()
        if '/' in linha:
            portugues, ingles = linha.split('/', 1)
            keyword = portugues
            list_content = create_content(keyword)
            duration = create_sound(list_content[2],keyword)
            files = search_video(keyword=ingles,duration=duration)
            compile_video(files,keyword)
            subtitle_video.subtitle_video(keyword)    
            upload_video.main(keyword + "_subtitled.mp4",list_content[4].replace('"',''),list_content[6].replace('"',''),list_content[8].replace('"',''),"public")
            print(list_content)

main()    


