from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from datetime import date, datetime

# Hardcoded corpus of focus topics, courses, and skills for content-based recommendation
RECOMMENDATION_CORPUS = [
    {
        "id": 1,
        "title": "Machine Learning & Deep Learning Fundamentals",
        "category": "Artificial Intelligence",
        "skills": "Python, Machine Learning, Deep Learning, Neural Networks, TensorFlow, PyTorch, Scikit-Learn",
        "description": "Learn the theory and implementation of core machine learning algorithms, deep learning models, and training techniques."
    },
    {
        "id": 2,
        "title": "Full-Stack Web Development Boot Camp",
        "category": "Software Engineering",
        "skills": "HTML, CSS, JavaScript, React, Node.js, Express, MongoDB, REST APIs, Git",
        "description": "Build dynamic, responsive web applications from front to back using HTML, CSS, JavaScript, and Node.js."
    },
    {
        "id": 3,
        "title": "Data Engineering and Pipelines",
        "category": "Data Science",
        "skills": "SQL, Python, Apache Spark, ETL, Data Warehousing, Data Pipelines, AWS, Docker",
        "description": "Design and build data architectures, ETL processes, and scale pipeline pipelines to manage massive datasets."
    },
    {
        "id": 4,
        "title": "Cloud Architecture & DevOps Essentials",
        "category": "Cloud & Infrastructure",
        "skills": "AWS, Docker, Kubernetes, CI/CD, Terraform, Linux, Shell Scripting, Security",
        "description": "Understand cloud systems architecture, containerization, container orchestration, and continuous deployment workflows."
    },
    {
        "id": 5,
        "title": "UI/UX Product Design & Prototyping",
        "category": "Design",
        "skills": "Figma, User Research, Wireframing, Prototyping, Visual Design, Information Architecture",
        "description": "Master user-centric design principles, conduct user research, and build interactive wireframes and prototypes."
    },
    {
        "id": 6,
        "title": "Introduction to Data Science & Analytics",
        "category": "Data Science",
        "skills": "R, Python, SQL, Tableau, Statistics, Probability, Data Visualization, Excel",
        "description": "Analyze data, perform statistical tests, build dashboards, and extract business insights from structured datasets."
    },
    {
        "id": 7,
        "title": "Mobile App Development with Flutter & Dart",
        "category": "Software Engineering",
        "skills": "Dart, Flutter, iOS, Android, State Management, Firebase, Mobile UI",
        "description": "Create cross-platform mobile apps for iOS and Android using Flutter's widget framework and Dart."
    },
    {
        "id": 8,
        "title": "Cybersecurity & Ethical Hacking Basics",
        "category": "Cybersecurity",
        "skills": "Network Security, Penetration Testing, Linux, Cryptography, OWASP Top 10, Firewalls",
        "description": "Identify vulnerabilities, secure computer networks, and learn standard hacking techniques and countermeasures."
    },
    {
        "id": 9,
        "title": "Advanced Data Structures & Algorithms",
        "category": "Computer Science",
        "skills": "Java, C++, Algorithms, Graphs, Dynamic Programming, Time Complexity, Tree Structures",
        "description": "Deep dive into advanced algorithmic design patterns, data structure optimizations, and competitive programming principles."
    },
    {
        "id": 10,
        "title": "Natural Language Processing and Large Language Models",
        "category": "Artificial Intelligence",
        "skills": "NLP, Transformers, HuggingFace, LLMs, Text Processing, PyTorch, Tokenization",
        "description": "Train and fine-tune large language models, build chatbots, and build applications utilizing modern NLP systems."
    }
]

def recommend_skills(career_objective: str, num_recommendations: int = 3):
    """
    Content-Based Skill Recommender:
    Uses TF-IDF Vectorizer and Cosine Similarity to compare the student's career objective
    with available training modules/courses in the corpus, returning the top matches.
    """
    if not career_objective:
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
    Routine Adjuster Heuristic:
    Evaluates logged study sessions to determine optimal sleep/energy conditions,
    calculates workload score from active tasks, and designs a customized, hour-by-hour
    study schedule optimized to avoid burnout and match peak focus periods.
    """
    # 1. Calculate Workload Score from Active Tasks
    # Active tasks are those whose status is not "completed"
    workload_score = 0.0
    pending_tasks_count = 0
    high_priority_count = 0
    
    for task in active_tasks:
        status = getattr(task, 'status', task.get('status', 'todo'))
        priority = getattr(task, 'priority', task.get('priority', 'medium'))
        
        if status in ["todo", "in_progress", "Pending", "In Progress"]:
            pending_tasks_count += 1
            if priority.lower() == "high":
                workload_score += 2.5
                high_priority_count += 1
            elif priority.lower() == "medium":
                workload_score += 1.5
            else:
                workload_score += 0.75
                
    # Calculate recommended daily study hours based on workload
    base_study_hours = 2.0
    recommended_study_hours = base_study_hours + (workload_score * 0.5)
    recommended_study_hours = min(max(recommended_study_hours, 2.0), 8.0) # Cap between 2 and 8 hours

    # 2. Analyze Sleep and Productivity from logs
    # Group logs by date to compute daily study hours
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
    avg_study_hours = np.mean(study_hours_list) if study_hours_list else 3.0
    
    # Calculate simulated sleep hours: assume sleep decreases slightly if study duration is very high
    # Let's map daily study hours to sleep hours
    sleep_list = []
    high_prod_sleep_list = []
    
    for log_date, mins in daily_study_mins.items():
        hours_studied = mins / 60.0
        # Estimate sleep hours
        est_sleep = 8.5 - (hours_studied * 0.15)
        # Clamp sleep between 5.0 and 9.0
        est_sleep = min(max(est_sleep, 5.0), 9.0)
        sleep_list.append(est_sleep)
        
        # Average productivity for this day
        avg_day_prod = np.mean(daily_productivities[log_date])
        if avg_day_prod >= 7.5:
            high_prod_sleep_list.append(est_sleep)
            
    avg_sleep = np.mean(sleep_list) if sleep_list else 7.5
    optimal_sleep = np.mean(high_prod_sleep_list) if high_prod_sleep_list else 8.0
    
    # Calculate sleep debt
    sleep_debt = optimal_sleep - avg_sleep
    
    if sleep_debt > 1.2:
        sleep_status = "Sleep Deprived"
        peak_focus = "Late Afternoon (16:00 - 18:00)"
        pomodoro_style = "Pomodoro: 40 mins study / 20 mins rest + Afternoon Power Nap"
        # Reduce study hours slightly if sleep deprived to preserve mental health
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

    # 3. Design Hour-by-Hour Schedule
    schedule = []
    
    # Morning Routine
    schedule.append({
        "time_slot": "07:00 - 08:30",
        "activity": "Morning Routine & Breakfast",
        "description": "Wake up, eat a nutritious breakfast, and hydrate."
    })
    schedule.append({
        "time_slot": "08:30 - 09:00",
        "activity": "Daily Planning & Review",
        "description": "Identify today's primary tasks and set focus goals."
    })
    
    # Distribute study hours into blocks
    remaining_study = recommended_study_hours
    
    # Morning Study Block
    if remaining_study >= 2.0:
        if sleep_status == "Sleep Deprived":
            # Sleep deprived students should do light admin or rest in the morning
            schedule.append({
                "time_slot": "09:00 - 11:00",
                "activity": "Light Study / Planning",
                "description": f"Read notes, plan tasks. Use {pomodoro_style}."
            })
            remaining_study -= 2.0
        else:
            block_time = min(2.5, remaining_study)
            schedule.append({
                "time_slot": "09:00 - 11:30",
                "activity": "Study Block 1: Deep Work (Peak Energy)",
                "description": f"Focus on high-priority tasks and complex problem solving. Use {pomodoro_style}."
            })
            remaining_study -= block_time
    else:
        schedule.append({
            "time_slot": "09:00 - 11:30",
            "activity": "Leisure / Reading",
            "description": "Read articles, catch up on news, or relax."
        })
        
    schedule.append({
        "time_slot": "11:30 - 13:00",
        "activity": "Admin Tasks & Mid-day Break",
        "description": "Handle emails, organize files, and relax."
    })
    
    schedule.append({
        "time_slot": "13:00 - 14:00",
        "activity": "Lunch & Social Time",
        "description": "Have a healthy lunch, chat with peers, or walk."
    })
    
    # Mid-day nap/rest adjustment for sleep debt
    if sleep_status == "Sleep Deprived":
        schedule.append({
            "time_slot": "14:00 - 14:45",
            "activity": "Rest & Power Nap",
            "description": "Highly recommended to recharge cognitive batteries."
        })
        afternoon_start = "14:45"
    elif sleep_status == "Mild Sleep Debt":
        schedule.append({
            "time_slot": "14:00 - 14:20",
            "activity": "Power Nap / Mindful Breathing",
            "description": "Quick rest to combat mid-day energy dip."
        })
        afternoon_start = "14:20"
    else:
        afternoon_start = "14:00"
        
    # Afternoon Study Block
    if remaining_study > 0:
        block_time = min(2.5, remaining_study)
        schedule.append({
            "time_slot": f"{afternoon_start} - 16:30",
            "activity": "Study Block 2: Collaborative / Applied Practice",
            "description": f"Assignments, coding, or discussion groups. {pomodoro_style}."
        })
        remaining_study -= block_time
    else:
        schedule.append({
            "time_slot": f"{afternoon_start} - 16:30",
            "activity": "Hobby / Personal Projects",
            "description": "Explore interests outside of curriculum."
        })
        
    schedule.append({
        "time_slot": "16:30 - 17:30",
        "activity": "Exercise / Outdoor Time",
        "description": "A light workout, run, or walk outside to boost circulation and mental clarity."
    })
    
    # Late Afternoon / Evening Study Block
    if remaining_study > 0:
        block_time = min(2.0, remaining_study)
        schedule.append({
            "time_slot": "17:30 - 19:00",
            "activity": "Study Block 3: Review & Homework",
            "description": f"Refine what was learned, work on minor assignments. {pomodoro_style}."
        })
        remaining_study -= block_time
    else:
        schedule.append({
            "time_slot": "17:30 - 19:00",
            "activity": "Social / Relaxation",
            "description": "Relax, watch a show, or socialize."
        })
        
    schedule.append({
        "time_slot": "19:00 - 20:30",
        "activity": "Dinner & Family/Friend Time",
        "description": "Wind down from academic commitments."
    })
    
    # Night Study Block
    if remaining_study > 0:
        schedule.append({
            "time_slot": "20:30 - 22:00",
            "activity": "Study Block 4: Gentle Review",
            "description": "Review vocabulary, flashcards, or prepare tasks for tomorrow. Do not start new topics."
        })
    else:
        schedule.append({
            "time_slot": "20:30 - 22:00",
            "activity": "Creative Play / Reading",
            "description": "Fiction reading, drawing, or light hobby."
        })
        
    schedule.append({
        "time_slot": "22:00 - 23:00",
        "activity": "Digital Detox & Sleep Prep",
        "description": "Turn off screens, meditate, or prepare for bed."
    })
    
    # Sleep
    schedule.append({
        "time_slot": "23:00 - 07:00",
        "activity": "Sleep",
        "description": f"Maintain a dark, cool environment. Aim for consistent wake up."
    })

    # Insights & Suggestions
    insights = []
    insights.append(f"Optimal sleep duration calculated from your peak productivity: {optimal_sleep:.1f} hours.")
    insights.append(f"Your recent average sleep is {avg_sleep:.1f} hours, putting you in a state of '{sleep_status}'.")
    
    if sleep_status == "Sleep Deprived":
        insights.append("Recommendation: High priority tasks should be deferred or handled slowly. We inserted a mandatory power nap and trimmed study hours to prevent cognitive fatigue.")
    elif sleep_status == "Mild Sleep Debt":
        insights.append("Recommendation: A short nap is scheduled to replenish mental reserves. Study in 50-minute blocks with 10-minute breaks to sustain energy.")
    else:
        insights.append("Recommendation: Excellent sleep hygiene! You are ready for Deep Work (90-minute blocks). Leverage your morning peak focus period for complex concepts.")
        
    insights.append(f"Workload score is {workload_score:.2f} based on {pending_tasks_count} pending task(s) (including {high_priority_count} high-priority tasks). We recommend {recommended_study_hours:.1f} study hours today.")

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
