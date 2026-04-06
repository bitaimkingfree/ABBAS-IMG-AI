from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

BASE_URL = "https://genpick.app"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json"
}


def create_job(prompt, num_images=2, aspect="1:1", style="diversity"):
    url = f"{BASE_URL}/api/imagen?async=true"
    payload = {
        "prompt": prompt,
        "aspectRatio": aspect,
        "numberOfImages": num_images,
        "style": style
    }

    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=15)
        data = r.json()
        return data.get("jobId")
    except:
        return None


def fetch_images(job_id):
    url = f"{BASE_URL}/api/imagen/jobs/{job_id}"

    for _ in range(15):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            data = r.json()

            if "images" in data and len(data["images"]) > 0:
                return data["images"]

        except:
            pass

        time.sleep(2)

    return []


@app.route('/generate', methods=['GET'])
def generate():
    prompt = request.args.get('prompt')
    num_images = int(request.args.get('num_images', 2))
    aspect = request.args.get('aspect', "1:1")
    style = request.args.get('style', "diversity")

    if not prompt:
        return jsonify({
            "success": False,
            "error": "Prompt is required"
        }), 400

    job_id = create_job(prompt, num_images, aspect, style)

    if not job_id:
        return jsonify({
            "success": False,
            "error": "Job creation failed"
        }), 500

    images = fetch_images(job_id)

    return jsonify({
        "success": True,
        "prompt": prompt,
        "job_id": job_id,
        "count": len(images),
        "images": images
    })


@app.route('/')
def home():
    return jsonify({
        "message": "🚀 Image Generator API running (Vercel Fixed)",
        "usage": "/generate?prompt=your_text"
    })


app = app
