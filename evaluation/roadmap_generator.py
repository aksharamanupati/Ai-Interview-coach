"""
7-Day Practice Roadmap Generator.
Builds a targeted daily training plan tailored to the candidate's discovered weaknesses.
"""
from typing import List, Dict, Any

ROADMAP_TEMPLATES = {
    "Structure": [
        {"day": "Day 1", "topic": "STAR Method Mastery", "activity": "Practice rewriting 3 past college/project experiences into clear Situation, Task, Action, Result bullets.", "target_metric": "State explicit actions within the first 30 seconds."},
        {"day": "Day 4", "topic": "Behavioral Conflict Alignment", "activity": "Record a 2-minute mock answer explaining how you resolved a team disagreement without blaming others.", "target_metric": "Include positive collaborative resolution."}
    ],
    "Technical Depth": [
        {"day": "Day 2", "topic": "Under-the-Hood Mechanics", "activity": "Review memory allocation, indexing algorithms, and big-O space/time tradeoffs for your primary language.", "target_metric": "Explain internal mechanics instead of surface API syntax."},
        {"day": "Day 5", "topic": "Architectural Bottlenecks & Caching", "activity": "Design a small microservice or database schema and list where failure points or race conditions might arise.", "target_metric": "Identify at least 2 potential architectural failure points."}
    ],
    "Specificity": [
        {"day": "Day 3", "topic": "Quantifiable Project Metrics", "activity": "Audit your resume projects: assign exact numbers (request latency, dataset size, test coverage) to each project.", "target_metric": "Cite at least 2 quantifiable data points per answer."},
        {"day": "Day 6", "topic": "Tooling and Diagnostics", "activity": "Practice answering: 'Walk me through a bug you fixed.' Name exact profiling and logging tools.", "target_metric": "Explicitly name tools (e.g., Postman, Git, Chrome DevTools, Pytest)."}
    ],
    "Clarity": [
        {"day": "Day 1", "topic": "Pacing & Elimination of Verbal Fillers", "activity": "Practice answering questions while deliberately taking 2-second silent pauses to think before speaking.", "target_metric": "Zero filler words ('um', 'basically') across 60 seconds."}
    ],
    "Relevance": [
        {"day": "Day 3", "topic": "First-Sentence Directness", "activity": "Practice answering the exact question within the first 10 words before expanding into background context.", "target_metric": "Directly answer the prompt in sentence #1."}
    ],
    "Conciseness": [
        {"day": "Day 4", "topic": "60-Second Elevator Responses", "activity": "Time your technical answers using a stopwatch to ensure you conclude between 60 and 90 seconds.", "target_metric": "Word count between 75 and 150 words."}
    ]
}

def generate_practice_roadmap(weaknesses: List[str], target_role: str = "Software Engineer") -> List[Dict[str, Any]]:
    """Generate a cohesive 7-day practice roadmap."""
    roadmap = []
    seen_days = set()
    
    # Priority matching based on identified weak dimensions
    day_counter = 1
    for w in weaknesses:
        for dim, tasks in ROADMAP_TEMPLATES.items():
            if dim.lower() in w.lower():
                for t in tasks:
                    if day_counter <= 6 and t["topic"] not in [r["topic"] for r in roadmap]:
                        roadmap.append({
                            "day": f"Day {day_counter}",
                            "topic": t["topic"],
                            "activity": t["activity"],
                            "target_metric": t["target_metric"]
                        })
                        day_counter += 1
                        if day_counter > 6:
                            break
                            
    # Fill remaining days up to Day 6 if needed
    default_plan = [
        {"day": f"Day {day_counter}", "topic": "Resume Project Walkthrough", "activity": "Practice explaining your primary project's architecture in 90 seconds.", "target_metric": "Cover frontend, backend, database, and deployment."},
        {"day": f"Day {day_counter+1}", "topic": "Core Data Structures & Algorithmic Tradeoffs", "activity": "Solve 2 problems focusing on verbal explanation of time/space complexity.", "target_metric": "State big-O before writing code."},
        {"day": f"Day {day_counter+2}", "topic": "Behavioral Competency & Team Dynamics", "activity": "Prepare answers for leadership, handling deadlines, and dealing with ambiguous requirements.", "target_metric": "Highlight proactive communication."},
        {"day": f"Day {day_counter+3}", "topic": "Domain & Tooling Deep Dive", "activity": "Prepare answers testing framework lifecycle and database querying optimizations.", "target_metric": "Deep dive into real-world use cases."},
        {"day": f"Day {day_counter+4}", "topic": "Timed Mock Interview Run", "activity": "Perform a complete 5-question voice session without reading from notes.", "target_metric": "Average session score > 75."}
    ]
    
    for item in default_plan:
        if day_counter <= 6:
            item["day"] = f"Day {day_counter}"
            roadmap.append(item)
            day_counter += 1

    # Day 7 is always the Final Full Assessment
    roadmap.append({
        "day": "Day 7",
        "topic": "Comprehensive Capstone Mock Interview",
        "activity": f"Run a complete 20-minute mock interview for the {target_role} role combining technical, project, and behavioral questions.",
        "target_metric": "Demonstrate resolved weaknesses from Session 1 with improved overall readiness."
    })
    
    return roadmap[:7]
