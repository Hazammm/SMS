from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import date, datetime, timedelta

# Focus topics, courses, and skills corpus for TF-IDF content-based skill recommendation
RECOMMENDATION_CORPUS = [
    {
        "id": 1,
        "title": "Machine Learning & Deep Learning Fundamentals",
        "category": "Artificial Intelligence",
        "skills": "Python, Machine Learning, Deep Learning, Neural Networks, TensorFlow, PyTorch, Scikit-Learn",
        "description": "Learn the theory and implementation of core machine learning algorithms, deep neural networks, and training pipelines."
    },
    {
        "id": 2,
        "title": "Full-Stack Web Development & Modern Frameworks",
        "category": "Software Engineering",
        "skills": "HTML, CSS, JavaScript, React, Node.js, Express, FastApi, MongoDB, REST APIs, Git",
        "description": "Build dynamic, responsive web applications from front to back using modern UI frameworks, RESTful endpoints, and backend architectures."
    },
    {
        "id": 3,
        "title": "Data Engineering & Scalable ETL Pipelines",
        "category": "Data Science",
        "skills": "SQL, Python, Apache Spark, ETL, Data Warehousing, Data Pipelines, AWS, Docker",
        "description": "Design and build data architectures, stream processing pipelines, and scalable warehouse systems for massive datasets."
    },
    {
        "id": 4,
        "title": "Cloud Architecture & DevOps Essentials",
        "category": "Cloud & Infrastructure",
        "skills": "AWS, Docker, Kubernetes, CI/CD, Terraform, Linux, Shell Scripting, Security",
        "description": "Master cloud infrastructure design, microservice containerization, container orchestration, and automated deployment pipelines."
    },
    {
        "id": 5,
        "title": "UI/UX Product Design & Design Systems",
        "category": "Design",
        "skills": "Figma, User Research, Wireframing, Prototyping, Visual Design, Information Architecture, Accessibility",
        "description": "Master user-centered design principles, conduct behavioral research, and craft interactive design systems and wireframes."
    },
    {
        "id": 6,
        "title": "Data Science, Analytics & Statistical Modeling",
        "category": "Data Science",
        "skills": "R, Python, SQL, Tableau, Statistics, Probability, Data Visualization, Excel, Pandas",
        "description": "Analyze multi-dimensional data, perform rigorous statistical tests, construct executive dashboards, and extract business insights."
    },
    {
        "id": 7,
        "title": "Cross-Platform Mobile App Development",
        "category": "Software Engineering",
        "skills": "Dart, Flutter, iOS, Android, State Management, Firebase, Mobile UI, React Native",
        "description": "Create fluid cross-platform mobile apps for iOS and Android using modern reactive UI toolkits and backend integrations."
    },
    {
        "id": 8,
        "title": "Cybersecurity & Ethical Hacking Systems",
        "category": "Cybersecurity",
        "skills": "Network Security, Penetration Testing, Linux, Cryptography, OWASP Top 10, Firewalls, Threat Analysis",
        "description": "Identify system vulnerabilities, harden cloud networks, and understand modern attack vectors and defensive security protocols."
    },
    {
        "id": 9,
        "title": "Advanced Data Structures & Algorithmic Optimization",
        "category": "Computer Science",
        "skills": "Java, C++, Algorithms, Graphs, Dynamic Programming, Time Complexity, Tree Structures, LeetCode",
        "description": "Deep dive into advanced algorithmic design patterns, data structure efficiency optimizations, and competitive problem solving."
    },
    {
        "id": 10,
        "title": "Natural Language Processing & LLM Engineering",
        "category": "Artificial Intelligence",
        "skills": "NLP, Transformers, HuggingFace, LLMs, Text Processing, PyTorch, Tokenization, Vector DBs",
        "description": "Fine-tune large language models, build generative AI agents, and implement semantic retrieval and NLP pipelines."
    }
]

def recommend_skills(career_objective: str, num_recommendations: int = 3) -> list:
    """
    Content-Based Skill Recommender:
    Uses TF-IDF Vectorization and Cosine Similarity to score the student's career objective
    against the training corpus, returning the top matching modules.
    """
    if not career_objective or not career_objective.strip():
        return []
    
    corpus_texts = []
    for item in RECOMMENDATION_CORPUS:
        text = f"{item['title']} {item['category']} {item['skills']} {item['description']}"
        corpus_texts.append(text)
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(corpus_texts)
    
    objective_vector = vectorizer.transform([career_objective])
    similarities = cosine_similarity(objective_vector, tfidf_matrix).flatten()
    
    top_indices = similarities.argsort()[::-1][:num_recommendations]
    
    results = []
    for idx in top_indices:
        score = float(similarities[idx])
        item = RECOMMENDATION_CORPUS[idx]
        results.append({
            "id": item["id"],
            "title": item["title"],
            "category": item["category"],
            "skills": [s.strip() for s in item["skills"].split(",")],
            "description": item["description"],
            "score": round(score, 4)
        })
    return results


def optimize_schedule(routine_logs: list, active_tasks: list) -> dict:
    """
    Adaptive Schedule Optimizer:
    Evaluates logged study sessions to determine optimal sleep and cognitive state,
    calculates workload score from active tasks, and constructs a burnout-aware daily schedule.
    """
    workload_score = 0.0
    pending_tasks_count = 0
    high_priority_count = 0
    
    for task in active_tasks:
        status = getattr(task, 'status', task.get('status', 'todo'))
        priority = getattr(task, 'priority', task.get('priority', 'medium'))
        
        if status in ["todo", "in_progress", "Pending", "In Progress"]:
            pending_tasks_count += 1
            p_lower = str(priority).lower()
            if p_lower == "high":
                workload_score += 2.5
                high_priority_count += 1
            elif p_lower == "medium":
                workload_score += 1.5
            else:
                workload_score += 0.75
                
    base_study_hours = 2.0
    recommended_study_hours = base_study_hours + (workload_score * 0.5)
    recommended_study_hours = min(max(recommended_study_hours, 2.0), 8.0)  # Clamp between 2 and 8 hours

    daily_study_mins = {}
    daily_productivities = {}
    
    for log in routine_logs:
        log_date = getattr(log, 'date', log.get('date', date.today().isoformat()))
        log_duration = getattr(log, 'duration', log.get('duration', 60))
        log_prod = getattr(log, 'productivity', log.get('productivity', 8))
        
        if log_date not in daily_study_mins:
            daily_study_mins[log_date] = 0
            daily_productivities[log_date] = []
        daily_study_mins[log_date] += log_duration
        daily_productivities[log_date].append(log_prod)
        
    study_hours_list = [mins / 60.0 for mins in daily_study_mins.values()]
    avg_study_hours = float(np.mean(study_hours_list)) if study_hours_list else 3.0
    
    sleep_list = []
    high_prod_sleep_list = []
    
    for log_date, mins in daily_study_mins.items():
        hours_studied = mins / 60.0
        est_sleep = 8.5 - (hours_studied * 0.15)
        est_sleep = min(max(est_sleep, 5.0), 9.0)
        sleep_list.append(est_sleep)
        
        avg_day_prod = float(np.mean(daily_productivities[log_date]))
        if avg_day_prod >= 7.5:
            high_prod_sleep_list.append(est_sleep)
            
    avg_sleep = float(np.mean(sleep_list)) if sleep_list else 7.5
    optimal_sleep = float(np.mean(high_prod_sleep_list)) if high_prod_sleep_list else 8.0
    
    sleep_debt = optimal_sleep - avg_sleep
    
    if sleep_debt > 1.2:
        sleep_status = "Sleep Deprived"
        peak_focus = "Late Afternoon (16:00 - 18:00)"
        pomodoro_style = "Pomodoro: 40 mins study / 20 mins rest + Afternoon Power Nap"
        recommended_study_hours = max(recommended_study_hours - 1.5, 2.0)
    elif sleep_debt > 0.4:
        sleep_status = "Mild Sleep Debt"
        peak_focus = "Afternoon (14:00 - 17:00)"
        pomodoro_style = "Pomodoro: 50 mins study / 10 mins break"
        recommended_study_hours = max(recommended_study_hours - 0.5, 2.0)
    else:
        sleep_status = "Healthy / Optimal Sleep"
        peak_focus = "Morning (09:00 - 12:00) & Afternoon (14:00 - 17:00)"
        pomodoro_style = "Deep Work: 90 mins study / 15 mins break"

    schedule = [
        {
            "time_slot": "07:00 - 08:30",
            "activity": "Morning Routine & Hydration",
            "description": "Wake up, eat a balanced breakfast, and prepare for the day."
        },
        {
            "time_slot": "08:30 - 09:00",
            "activity": "Daily Planning & Focus Alignment",
            "description": "Review priorities and organize workspace for active study blocks."
        }
    ]
    
    remaining_study = recommended_study_hours
    
    if remaining_study >= 2.0:
        if sleep_status == "Sleep Deprived":
            schedule.append({
                "time_slot": "09:00 - 11:00",
                "activity": "Light Study / Review Session",
                "description": f"Read lecture slides and revise notes. Use {pomodoro_style}."
            })
            remaining_study -= 2.0
        else:
            block_time = min(2.5, remaining_study)
            schedule.append({
                "time_slot": "09:00 - 11:30",
                "activity": "Study Block 1: Deep Focus Work",
                "description": f"Target high-priority coursework and algorithm implementations. {pomodoro_style}."
            })
            remaining_study -= block_time
    else:
        schedule.append({
            "time_slot": "09:00 - 11:30",
            "activity": "Curriculum Exploration & Reading",
            "description": "Read tech articles, research topics, or explore documentation."
        })
        
    schedule.append({
        "time_slot": "11:30 - 13:00",
        "activity": "Administrative Tasks & Mid-day Recess",
        "description": "Organize study material, reply to messages, and unwind."
    })
    
    schedule.append({
        "time_slot": "13:00 - 14:00",
        "activity": "Lunch & Physical Mobility",
        "description": "Nutritious lunch and light outdoor walking."
    })
    
    if sleep_status == "Sleep Deprived":
        schedule.append({
            "time_slot": "14:00 - 14:45",
            "activity": "Rest & Power Nap",
            "description": "Essential power nap to restore cognitive alertness."
        })
        afternoon_start = "14:45"
    elif sleep_status == "Mild Sleep Debt":
        schedule.append({
            "time_slot": "14:00 - 14:20",
            "activity": "Power Nap / Mindfulness",
            "description": "Quick relaxation session to overcome afternoon dip."
        })
        afternoon_start = "14:20"
    else:
        afternoon_start = "14:00"
        
    if remaining_study > 0:
        block_time = min(2.5, remaining_study)
        schedule.append({
            "time_slot": f"{afternoon_start} - 16:30",
            "activity": "Study Block 2: Hands-on Projects & Coding",
            "description": f"Practical assignments and lab problem solving. {pomodoro_style}."
        })
        remaining_study -= block_time
    else:
        schedule.append({
            "time_slot": f"{afternoon_start} - 16:30",
            "activity": "Personal Learning & Side Projects",
            "description": "Explore personal coding interests outside school."
        })
        
    schedule.append({
        "time_slot": "16:30 - 17:30",
        "activity": "Physical Exercise & Outdoors",
        "description": "Cardio, gym, or walking to recharge energy levels."
    })
    
    if remaining_study > 0:
        block_time = min(2.0, remaining_study)
        schedule.append({
            "time_slot": "17:30 - 19:00",
            "activity": "Study Block 3: Assignment Polish & Review",
            "description": f"Double-check homework, practice set problems. {pomodoro_style}."
        })
        remaining_study -= block_time
    else:
        schedule.append({
            "time_slot": "17:30 - 19:00",
            "activity": "Social Connection & Leisure",
            "description": "Relax with friends or enjoy creative hobbies."
        })
        
    schedule.append({
        "time_slot": "19:00 - 20:30",
        "activity": "Dinner & Leisure Time",
        "description": "Wind down academic commitments for the evening."
    })
    
    if remaining_study > 0:
        schedule.append({
            "time_slot": "20:30 - 22:00",
            "activity": "Study Block 4: Light Flashcards & Reading",
            "description": "Review key terms and formulas. Avoid heavy new concepts before bed."
        })
    else:
        schedule.append({
            "time_slot": "20:30 - 22:00",
            "activity": "Reading / Creative Play",
            "description": "Read fiction, listen to music, or relax."
        })
        
    schedule.append({
        "time_slot": "22:00 - 23:00",
        "activity": "Digital Detox & Evening Wind-down",
        "description": "Disconnect from screens, prepare for a restful sleep."
    })
    
    schedule.append({
        "time_slot": "23:00 - 07:00",
        "activity": "Sleep",
        "description": "Restful sleep in a dark, quiet environment."
    })

    insights = [
        f"Optimal sleep calculated for peak cognitive output: {optimal_sleep:.1f} hours.",
        f"Recent average sleep estimated at {avg_sleep:.1f} hours ({sleep_status})."
    ]
    
    if sleep_status == "Sleep Deprived":
        insights.append("Notice: Mandatory power nap inserted and study load trimmed to prevent burnout.")
    elif sleep_status == "Mild Sleep Debt":
        insights.append("Notice: Short rest interval scheduled. Recommend 50-min study blocks with 10-min breaks.")
    else:
        insights.append("Notice: Excellent cognitive status! Deep Work blocks (90 min) enabled.")
        
    insights.append(f"Workload score is {workload_score:.2f} based on {pending_tasks_count} pending tasks ({high_priority_count} high priority). Recommended study duration: {recommended_study_hours:.1f} hours.")

    return {
        "optimal_sleep_hours": round(optimal_sleep, 2),
        "recent_sleep_hours_avg": round(avg_sleep, 2),
        "sleep_status": sleep_status,
        "calculated_workload_score": round(workload_score, 2),
        "recommended_daily_study_hours": round(recommended_study_hours, 2),
        "peak_focus_period": peak_focus,
        "pomodoro_style": pomodoro_style,
        "schedule": schedule,
        "insights": insights
    }
