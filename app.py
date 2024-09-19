from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Constants for job roles, experiences, and locations
roles = [
    "Software Engineer", "Data Scientist", "Product Manager", "UX Designer", 
    "DevOps Engineer", "Backend Developer", "Frontend Developer", "Full Stack Developer", 
    "Mobile App Developer", "Cybersecurity Specialist", "Cloud Engineer", 
    "AI/ML Engineer", "Blockchain Developer", "QA Engineer", "Database Administrator"
]

experiences = ["0-2 years", "2-5 years", "5-10 years", "10+ years"]

locations = [
    "All", "Bangalore, Karnataka", "Hyderabad, Telangana", "Pune, Maharashtra", 
    "Mumbai, Maharashtra", "Chennai, Tamil Nadu", "Delhi, Delhi", 
    "Gurgaon, Haryana", "Noida, Uttar Pradesh", "Kolkata, West Bengal", 
    "Ahmedabad, Gujarat", "Remote"
]

# Example Adzuna and Jobble job fetching functions
def fetch_jobble_jobs(role, experience):
    base_url = "https://jooble.org/api/56386444-f128-4415-8df6-97dbbf2a401e"  # Replace with your actual API key
    location = "India"
    
    # Map experience to role keyword
    experience_keywords = {
        "0-2 years": "0-2 years",
        "2-5 years": "2-5 years",
        "5-10 years": "5-10 years",
        "10+ years": "10+ years"
    }
    
    keyword = f"{experience_keywords[experience]} {role}"
    
    params = {
        "keywords": keyword,
        "location": location,
        "page": 1,
    }
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.post(base_url, json=params, headers=headers)
    
    jobs = []
    if response.status_code == 200:
        job_results = response.json().get('jobs', [])
        for job in job_results:
            jobs.append({
                'Title': job.get('title', 'N/A'),
                'Company': job.get('company', 'N/A'),
                'Location': job.get('location', 'N/A'),
                'Link': job.get('link', '#'),
                'Updated': job.get('updated', 'N/A')
            })
    return jobs

ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/in/search/1"
APP_ID = "2555e2f7"
APP_KEY = "8a4d6ee7e9b93c1fa12c78aa1e62fc0d"

def fetch_adzuna_jobs(role, experience, location):
    if location.lower() == 'all':
        location = 'India'
    
    # Combine role and experience into the search query
    search_query = f"{experience} {role}"
    
    params = {
        'app_id': APP_ID,
        'app_key': APP_KEY,
        'what': search_query,
        'where': location,
        'max_days_old': 30,
        'content-type': 'application/json'
    }

    response = requests.get(ADZUNA_API_URL, params=params)
    jobs_data = response.json()
    
    jobs = []
    for job in jobs_data.get('results', []):
        jobs.append({
            'Title': job.get('title', 'N/A'),
            'Company': job.get('company', {}).get('display_name', 'N/A'),
            'Location': job.get('location', {}).get('display_name', 'N/A'),
            'Link': job.get('redirect_url', '#')
        })
    
    return jobs


# Aggregate jobs from different sources
def aggregate_jobs(role, experience, location):
    adzuna_jobs = fetch_adzuna_jobs(role, experience, location)
    jobble_jobs = fetch_jobble_jobs(role, experience) 
    all_jobs = adzuna_jobs + jobble_jobs
    return all_jobs

# Endpoint for job search
@app.route('/jobs', methods=['POST'])
def job_search():
    if request.method == 'POST':
        data = request.get_json()  # Use JSON payload instead of form
        role = data.get('role')
        experience = data.get('experience')
        location = data.get('location')
        
        # Aggregate jobs from sources
        jobs = aggregate_jobs(role, experience, location)
        
        # Return the jobs as JSON response
        return jsonify({"jobs": jobs, "role": role, "experience": experience, "location": location}), 200
    
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    # Run the Flask app, binding to all interfaces (0.0.0.0) to make it accessible via local network
    app.run(host='0.0.0.0', port=5000, debug=True)