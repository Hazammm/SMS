/* ==========================================================================
   AuraSMS APPLICATION LOGIC (app.js)
   ========================================================================== */

// --- Global Application State ---
const state = {
    courses: [],
    tasks: [],
    routineLogs: [],
    targetSkills: [],
    isDemoMode: true,
    apiBase: (typeof window !== 'undefined' && (window.location.origin.includes('localhost') || window.location.origin.includes('127.0.0.1'))) 
               ? `${window.location.origin}/api` 
               : 'http://127.0.0.1:8000/api'
};

// --- Mock Preloaded Data (For Offline Standalone Demo Mode) ---
const MOCK_DATA = {
    courses: [
        { id: "c1", code: "CS-401", name: "Artificial Intelligence & Neural Networks", credits: 3, grade: "A", gpa: 4.00 },
        { id: "c2", code: "CS-302", name: "Data Structures and Algorithms", credits: 4, grade: "A-", gpa: 3.70 },
        { id: "c3", code: "CS-305", name: "Database Management Systems", credits: 3, grade: "B+", gpa: 3.30 },
        { id: "c4", code: "MAT-201", name: "Linear Algebra & Applications", credits: 3, grade: "A", gpa: 4.00 },
        { id: "c5", code: "CS-499", name: "Capstone Project Phase I", credits: 3, grade: "IP", gpa: 4.00 }
    ],
    tasks: [
        { id: "t1", title: "Implement backpropagation neural network in NumPy", description: "Write feedforward, cost computation, and gradient updates manually for a 3-layer net.", priority: "high", category: "assignment", due_date: getFutureDate(1), status: "in_progress" },
        { id: "t2", title: "Design database schema for Capstone eCommerce project", description: "Draw Entity-Relationship diagrams and prepare SQL DDL schemas for PostgreSQL.", priority: "medium", category: "project", due_date: getFutureDate(3), status: "todo" },
        { id: "t3", title: "Review lectures on Linear Algebra eigenvalues/eigenvectors", description: "Prepare notes on principal component analysis applications.", priority: "medium", category: "study", due_date: getFutureDate(5), status: "todo" },
        { id: "t4", title: "Midterm Exam Prep - Graph algorithms & complex traversal", description: "Revise BFS, DFS, Dijkstra, Bellman-Ford, and Minimum Spanning Trees.", priority: "high", category: "exam", due_date: getFutureDate(2), status: "todo" },
        { id: "t5", title: "Resolve LeetCode 3 Sum and sliding window problems", description: "Complete at least 5 medium-difficulty arrays/string interview questions.", priority: "low", category: "study", due_date: getFutureDate(-1), status: "completed" }
    ],
    routineLogs: [
        { id: "r1", activity: "Deep Work: Backpropagation Neural Net Coding", duration: 120, productivity: 9, date: getFutureDate(0), category: "project" },
        { id: "r2", activity: "Lecture: Database Systems normalization study", duration: 90, productivity: 8, date: getFutureDate(0), category: "study" },
        { id: "r3", activity: "Midterm Revision: Practice Exam Session", duration: 150, productivity: 7, date: getFutureDate(-1), category: "revision" },
        { id: "r4", activity: "Linear Algebra: Problem sets on eigenvectors", duration: 60, productivity: 9, date: getFutureDate(-2), category: "study" },
        { id: "r5", activity: "Capstone Team Standup & Backlog Grooming", duration: 45, productivity: 6, date: getFutureDate(-2), category: "class" }
    ],
    targetSkills: [
        { id: "s1", name: "Deep Learning (PyTorch)", progress: 65, goal: "AI Engineer" },
        { id: "s2", name: "Relational DB Normalization", progress: 85, goal: "Database Systems" },
        { id: "s3", name: "Docker Containerization", progress: 30, goal: "DevOps Architect" }
    ],
    schedule: [
        { time: "08:30 - 10:00", title: "Cognitive Peak: Deep Study Focus", desc: "Machine Learning theoretical derivations and math proofs.", type: "study" },
        { time: "10:00 - 10:20", title: "Tactical Break", desc: "Hydration, light stretching, screen off.", type: "break" },
        { time: "10:20 - 12:30", title: "Technical Application Work", desc: "Coding tasks for Capstone Project & Python assignments.", type: "project" },
        { time: "12:30 - 14:00", title: "Recess & Cognitive Reset", desc: "Lunch and physical walk outdoors.", type: "break" },
        { time: "14:00 - 15:30", title: "Systems Review & DBMS", desc: "Database query writing and theory revision.", type: "study" },
        { time: "15:30 - 15:50", title: "Afternoon Refreshment", desc: "Quick snack or mindfulness meditation.", type: "break" },
        { time: "15:50 - 17:30", title: "Active Recall & Mock Interview prep", desc: "Solving algorithmic problems and review exercises.", type: "study" }
    ]
};

// --- Chart Instances ---
let gpaChartInstance = null;
let productivityChartInstance = null;

// --- Initialize App ---
document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    initModals();
    await checkBackendConnection();
    await loadInitialData();
    initForms();
    initCharts();
    
    // Quick Event Listeners
    document.getElementById('generate-schedule-btn').addEventListener('click', optimizeSchedule);
    document.getElementById('btn-recommend-skills').addEventListener('click', generateAISkills);
    
    // Setup Skill suggestions
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            document.getElementById('career-goal').value = chip.textContent;
        });
    });

    // Setup tab redirects from dashboard cards
    document.querySelectorAll('.btn-view-tab').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetTab = e.currentTarget.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });

    // Setup search filter events
    document.getElementById('courses-search').addEventListener('input', renderCourses);

    // Category filter toggle events
    document.querySelectorAll('.btn-filter').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.btn-filter').forEach(el => el.classList.remove('active'));
            e.target.classList.add('active');
            renderTasks();
        });
    });
});

// --- Helper Date Creator ---
function getFutureDate(daysOffset) {
    const d = new Date();
    d.setDate(d.getDate() + daysOffset);
    return d.toISOString().split('T')[0];
}

// --- Navigation Controller ---
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update Sidebar Navigation highlights
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const targetNav = document.querySelector(`.nav-item[data-tab="${tabName}"]`);
    if (targetNav) targetNav.classList.add('active');

    // Toggle Content Sections
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    const targetTab = document.getElementById(`tab-${tabName}`);
    if (targetTab) targetTab.classList.add('active');

    // Update Header Text
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');
    
    switch(tabName) {
        case 'overview':
            pageTitle.textContent = 'Overview';
            pageSubtitle.textContent = 'Welcome back! Here is your academic performance at a glance.';
            updateCharts();
            break;
        case 'courses':
            pageTitle.textContent = 'Academic Courses';
            pageSubtitle.textContent = 'Manage your curriculum, track credits, and calculate term GPA.';
            break;
        case 'tasks':
            pageTitle.textContent = 'Task Board';
            pageSubtitle.textContent = 'Kanban workflow with drag-and-drop card status updates.';
            break;
        case 'routine':
            pageTitle.textContent = 'Routine & Planner';
            pageSubtitle.textContent = 'Log actual study times and review cognitive schedule peak analysis.';
            break;
        case 'skills':
            pageTitle.textContent = 'Skill Recommender AI';
            pageSubtitle.textContent = 'Generate highly customized roadmap plans utilizing AI capabilities.';
            break;
    }
}

// --- API Client Wrapper & Backend Checker ---
async function checkBackendConnection() {
    const badge = document.getElementById('connection-badge');
    const text = badge.querySelector('.status-text');
    
    try {
        const response = await fetch(`${state.apiBase}/health`, { method: 'GET', signal: AbortSignal.timeout(3000) });
        if (response.ok) {
            state.isDemoMode = false;
            badge.className = 'connection-status online';
            text.textContent = 'API Connected';
            showToast('Connected to FastAPI Backend API successfully!', 'success');
        } else {
            throw new Error();
        }
    } catch {
        state.isDemoMode = true;
        badge.className = 'connection-status offline';
        text.textContent = 'Demo Mode (Offline)';
        showToast('FastAPI Backend offline. Running in standalone Demo Mode.', 'warning');
    }
}

async function requestAPI(endpoint, method = 'GET', body = null) {
    if (state.isDemoMode) {
        // Fallback to reading and writing via LocalStorage
        return handleLocalStorageFallback(endpoint, method, body);
    }
    
    try {
        const headers = { 'Content-Type': 'application/json' };
        const options = { method, headers };
        if (body) options.body = JSON.stringify(body);
        
        const response = await fetch(`${state.apiBase}${endpoint}`, options);
        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        return await response.json();
    } catch (e) {
        console.error(`API Call failed on: ${endpoint}. Switching to LocalStorage fallback.`, e);
        state.isDemoMode = true;
        
        const badge = document.getElementById('connection-badge');
        badge.className = 'connection-status offline';
        badge.querySelector('.status-text').textContent = 'Demo Mode (Offline)';
        showToast('Lost connection to backend. Reverted to Standalone Mode.', 'danger');
        
        return handleLocalStorageFallback(endpoint, method, body);
    }
}

// --- LocalStorage Fallback Handler ---
function handleLocalStorageFallback(endpoint, method, body) {
    const getStorage = (key) => JSON.parse(localStorage.getItem(`aura_${key}`)) || MOCK_DATA[key];
    const setStorage = (key, data) => localStorage.setItem(`aura_${key}`, JSON.stringify(data));
    
    // Parse endpoints
    if (endpoint.startsWith('/courses')) {
        let list = getStorage('courses');
        if (method === 'GET') return list;
        if (method === 'POST') {
            const newItem = { id: `c_${Date.now()}`, ...body };
            list.push(newItem);
            setStorage('courses', list);
            return newItem;
        }
        if (method === 'DELETE') {
            const courseId = endpoint.split('/').pop();
            list = list.filter(c => c.id !== courseId);
            setStorage('courses', list);
            return { status: "success" };
        }
    }
    
    if (endpoint.startsWith('/tasks')) {
        let list = getStorage('tasks');
        if (method === 'GET') return list;
        if (method === 'POST') {
            const newItem = { id: `t_${Date.now()}`, ...body };
            list.push(newItem);
            setStorage('tasks', list);
            return newItem;
        }
        if (method.startsWith('PUT')) {
            const taskId = endpoint.split('/').pop();
            list = list.map(t => t.id === taskId ? { ...t, ...body } : t);
            setStorage('tasks', list);
            return list.find(t => t.id === taskId);
        }
        if (method === 'DELETE') {
            const taskId = endpoint.split('/').pop();
            list = list.filter(t => t.id !== taskId);
            setStorage('tasks', list);
            return { status: "success" };
        }
    }
    
    if (endpoint.startsWith('/routine')) {
        let list = getStorage('routineLogs');
        if (method === 'GET') return list;
        if (method === 'POST') {
            const newItem = { id: `r_${Date.now()}`, ...body };
            list.push(newItem);
            setStorage('routineLogs', list);
            return newItem;
        }
        if (method === 'DELETE') {
            const logId = endpoint.split('/').pop();
            list = list.filter(r => r.id !== logId);
            setStorage('routineLogs', list);
            return { status: "success" };
        }
    }

    if (endpoint.startsWith('/skills/targets')) {
        let list = getStorage('targetSkills');
        if (method === 'GET') return list;
        if (method === 'POST') {
            const newItem = { id: `s_${Date.now()}`, progress: 0, ...body };
            list.push(newItem);
            setStorage('targetSkills', list);
            return newItem;
        }
        if (method.startsWith('PUT')) {
            const skillId = endpoint.split('/').pop();
            list = list.map(s => s.id === skillId ? { ...s, ...body } : s);
            setStorage('targetSkills', list);
            return list.find(s => s.id === skillId);
        }
        if (method === 'DELETE') {
            const skillId = endpoint.split('/').pop();
            list = list.filter(s => s.id !== skillId);
            setStorage('targetSkills', list);
            return { status: "success" };
        }
    }
    
    if (endpoint.startsWith('/schedule/daily')) {
        return getStorage('schedule');
    }
    
    return null;
}

// --- Data Loader ---
async function loadInitialData() {
    try {
        state.courses = await requestAPI('/courses');
        state.tasks = await requestAPI('/tasks');
        state.routineLogs = await requestAPI('/routine');
        state.targetSkills = await requestAPI('/skills/targets');
        
        renderCourses();
        renderTasks();
        renderRoutineLogs();
        renderSmartSchedule();
        renderTargetSkills();
        updateGlobalStats();
    } catch(e) {
        console.error("Initial data load error: ", e);
    }
}

// --- Global Metrics Logic ---
function updateGlobalStats() {
    // 1. GPA Calculation
    const completedCourses = state.courses.filter(c => c.grade !== 'IP');
    let totalCredits = 0;
    let totalGPAPoints = 0;
    
    completedCourses.forEach(c => {
        totalCredits += Number(c.credits);
        totalGPAPoints += (Number(c.gpa) * Number(c.credits));
    });
    
    const computedGPA = totalCredits > 0 ? (totalGPAPoints / totalCredits).toFixed(2) : '0.00';
    
    // Update labels
    document.getElementById('header-gpa').textContent = computedGPA;
    document.getElementById('metric-gpa').textContent = computedGPA;
    
    // 2. Study Hours Sum
    const totalMinutes = state.routineLogs.reduce((acc, log) => acc + Number(log.duration), 0);
    const totalHours = (totalMinutes / 60).toFixed(1);
    
    document.getElementById('header-study-hours').textContent = `${totalHours}h`;
    document.getElementById('metric-study-hours').textContent = `${totalHours}h`;
    
    // 3. Task Completion Rate
    const completedTasks = state.tasks.filter(t => t.status === 'completed').length;
    const totalTasks = state.tasks.length;
    const taskRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;
    
    document.getElementById('header-tasks').textContent = `${taskRate}%`;
    document.getElementById('metric-task-rate').textContent = `${taskRate}%`;
    
    // 4. Target Skills Count
    document.getElementById('metric-skills').textContent = state.targetSkills.length;
}

// --- Dynamic Rendering: 1. Courses Section ---
function renderCourses() {
    const grid = document.getElementById('courses-grid');
    const searchVal = document.getElementById('courses-search').value.toLowerCase();
    
    grid.innerHTML = '';
    
    const filteredCourses = state.courses.filter(c => 
        c.name.toLowerCase().includes(searchVal) || c.code.toLowerCase().includes(searchVal)
    );
    
    if (filteredCourses.length === 0) {
        grid.innerHTML = `
            <div class="glass-panel" style="grid-column: 1/-1; padding: 40px; text-align: center; color: var(--text-muted);">
                <i class="fa-solid fa-folder-open" style="font-size: 32px; margin-bottom: 12px;"></i>
                <p>No courses found. Click 'Add Course' to register your first subject.</p>
            </div>
        `;
        return;
    }
    
    filteredCourses.forEach(course => {
        const card = document.createElement('div');
        card.className = 'course-card glass-panel';
        card.innerHTML = `
            <div class="course-card-header">
                <span class="course-code-badge">${course.code}</span>
                <div class="course-actions">
                    <button class="btn-card-action" onclick="deleteCourse('${course.id}')" title="Delete Course">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="course-card-body">
                <h3>${course.name}</h3>
                <p class="credits">${course.credits} Credit Hours</p>
            </div>
            <div class="course-card-footer">
                <div class="course-gpa-container">
                    <span class="course-gpa-val">${Number(course.gpa).toFixed(2)}</span>
                    <span class="course-gpa-label">GPA</span>
                </div>
                <span class="course-grade-badge ${course.grade === 'IP' ? 'ip' : ''}">
                    ${course.grade}
                </span>
            </div>
        `;
        grid.appendChild(card);
    });
}

async function deleteCourse(id) {
    if (confirm('Are you sure you want to delete this course?')) {
        await requestAPI(`/courses/${id}`, 'DELETE');
        state.courses = state.courses.filter(c => c.id !== id);
        renderCourses();
        updateGlobalStats();
        updateCharts();
        showToast('Course removed successfully.', 'info');
    }
}

// --- Dynamic Rendering: 2. Tasks Kanban Board ---
function renderTasks() {
    const todoCards = document.getElementById('todo-cards');
    const inprogressCards = document.getElementById('inprogress-cards');
    const completedCards = document.getElementById('completed-cards');
    
    todoCards.innerHTML = '';
    inprogressCards.innerHTML = '';
    completedCards.innerHTML = '';
    
    // Category filters
    const activeFilter = document.querySelector('.btn-filter.active').getAttribute('data-filter');
    const filteredTasks = activeFilter === 'all' 
        ? state.tasks 
        : state.tasks.filter(t => t.category === activeFilter);
        
    const counts = { todo: 0, in_progress: 0, completed: 0 };
    
    filteredTasks.forEach(task => {
        counts[task.status]++;
        
        const card = document.createElement('div');
        card.className = `task-card glass-panel ${task.priority}`;
        card.draggable = true;
        card.id = `task-${task.id}`;
        card.setAttribute('ondragstart', `drag(event, '${task.id}')`);
        
        card.innerHTML = `
            <div class="task-header">
                <span class="task-category">${task.category}</span>
                <span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority}</span>
            </div>
            <h4>${task.title}</h4>
            <p>${task.description || 'No description provided.'}</p>
            <div class="task-footer">
                <span class="task-due">
                    <i class="fa-regular fa-calendar"></i> ${formatDate(task.due_date)}
                </span>
                <div class="task-actions">
                    ${task.status !== 'completed' ? `
                        <button class="btn-task-action" onclick="moveTaskToNextStatus('${task.id}', '${task.status}')" title="Advance Stage">
                            <i class="fa-solid fa-chevron-right"></i>
                        </button>
                    ` : ''}
                    <button class="btn-task-action delete" onclick="deleteTask('${task.id}')" title="Delete Task">
                        <i class="fa-solid fa-circle-minus"></i>
                    </button>
                </div>
            </div>
        `;
        
        if (task.status === 'todo') todoCards.appendChild(card);
        else if (task.status === 'in_progress') inprogressCards.appendChild(card);
        else if (task.status === 'completed') completedCards.appendChild(card);
    });
    
    // Update Counter badges
    document.getElementById('todo-count').textContent = counts.todo;
    document.getElementById('inprogress-count').textContent = counts.in_progress;
    document.getElementById('completed-count').textContent = counts.completed;
    
    // Also render the quick tasks overview on the overview dashboard
    renderQuickTasksPeek();
}

function getPriorityBadgeClass(priority) {
    if (priority === 'high') return 'badge-magenta';
    if (priority === 'medium') return 'badge-gold';
    return 'badge-cyan';
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Kanban Drag and Drop Logic
if (typeof window !== 'undefined') {
    window.allowDrop = function(ev) {
        ev.preventDefault();
    }

    window.drag = function(ev, id) {
        ev.dataTransfer.setData("text", id);
    }

    window.drop = async function(ev, status) {
        ev.preventDefault();
        const id = ev.dataTransfer.getData("text");
        await updateTaskStatus(id, status);
    }
}

async function moveTaskToNextStatus(id, currentStatus) {
    const nextStatus = currentStatus === 'todo' ? 'in_progress' : 'completed';
    await updateTaskStatus(id, nextStatus);
}

async function updateTaskStatus(id, newStatus) {
    const task = state.tasks.find(t => t.id === id);
    if (!task) return;
    
    task.status = newStatus;
    await requestAPI(`/tasks/${id}`, 'PUT', { status: newStatus });
    
    renderTasks();
    updateGlobalStats();
}

async function deleteTask(id) {
    if (confirm('Are you sure you want to delete this task?')) {
        await requestAPI(`/tasks/${id}`, 'DELETE');
        state.tasks = state.tasks.filter(t => t.id !== id);
        renderTasks();
        updateGlobalStats();
        showToast('Task deleted.', 'info');
    }
}

// --- Dynamic Rendering: 3. Routine Session Logger & Smart Calendar ---
function renderRoutineLogs() {
    const list = document.getElementById('routine-logs-list');
    list.innerHTML = '';
    
    if (state.routineLogs.length === 0) {
        list.innerHTML = `<p style="padding: 10px; text-align: center; color: var(--text-muted); font-size:13px;">No tracked sessions yet.</p>`;
        return;
    }
    
    // Sort logs descending by date
    const sortedLogs = [...state.routineLogs].sort((a, b) => new Date(b.date) - new Date(a.date));
    
    sortedLogs.forEach(log => {
        const item = document.createElement('div');
        item.className = 'routine-list-item';
        item.innerHTML = `
            <div class="routine-list-details">
                <h5>${log.activity}</h5>
                <p>${log.duration} min • ${formatDate(log.date)} • <span style="text-transform: capitalize;">${log.category}</span></p>
            </div>
            <div class="routine-productivity-tag">
                <span class="prod-score ${getProductivityClass(log.productivity)}">
                    Focus: ${log.productivity}/10
                </span>
                <button class="btn-delete-session" onclick="deleteRoutineLog('${log.id}')" title="Delete Log">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        `;
        list.appendChild(item);
    });
}

function getProductivityClass(score) {
    if (score >= 9) return 'excellent';
    if (score >= 7) return 'good';
    if (score >= 5) return 'avg';
    return 'poor';
}

async function deleteRoutineLog(id) {
    if (confirm('Delete this logged activity session?')) {
        await requestAPI(`/routine/${id}`, 'DELETE');
        state.routineLogs = state.routineLogs.filter(r => r.id !== id);
        renderRoutineLogs();
        updateGlobalStats();
        updateCharts();
        showToast('Study session log removed.', 'info');
    }
}

// Smart Schedule Builder / Optimizer
async function renderSmartSchedule(customSchedule = null) {
    const timeline = document.getElementById('schedule-timeline');
    timeline.innerHTML = '';
    
    const scheduleItems = customSchedule || MOCK_DATA.schedule;
    
    // Update dates
    const currentDate = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
    document.getElementById('schedule-current-date').textContent = currentDate;
    
    scheduleItems.forEach(item => {
        const node = document.createElement('div');
        node.className = 'timeline-item';
        node.innerHTML = `
            <div class="timeline-time">${item.time}</div>
            <div class="timeline-title">${item.title}</div>
            <div class="timeline-desc">${item.desc}</div>
        `;
        timeline.appendChild(node);
    });
    
    // Also update overview dashboard quick peek
    renderQuickSchedulePeek(scheduleItems);
}

async function optimizeSchedule() {
    const btn = document.getElementById('generate-schedule-btn');
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Synthesizing...`;
    btn.disabled = true;
    
    // Simulate AI Optimization
    setTimeout(async () => {
        try {
            // Check API
            let optimized = null;
            if (!state.isDemoMode) {
                const response = await fetch(`${state.apiBase}/schedule/daily`);
                if (response.ok) optimized = await response.json();
            }
            
            // If offline or failed, generate mock optimized variation
            if (!optimized) {
                optimized = [
                    { time: "08:00 - 09:30", title: " Peak Mindset: High Concentration Study", desc: "Solve algorithmic complexity models. Ideal focus window.", type: "study" },
                    { time: "09:30 - 09:50", title: " Mindful Relaxation", desc: "Short recovery interval. Stay hydrated.", type: "break" },
                    { time: "09:50 - 12:00", title: " Active Coding & Application", desc: "Work on capstone architecture code block.", type: "project" },
                    { time: "12:00 - 13:30", title: " Nutritional Reset Break", desc: "Healthy lunch & motor cortex decompression.", type: "break" },
                    { time: "13:30 - 15:00", title: " Academic Reading & Comprehension", desc: "Course review and database query writing.", type: "study" },
                    { time: "15:00 - 15:20", title: " Active Regeneration", desc: "Quick walk, physical workout.", type: "break" },
                    { time: "15:20 - 17:00", title: " Synthetic Integration Session", desc: "Formulate target skill roadmaps and review.", type: "study" }
                ];
            }
            
            renderSmartSchedule(optimized);
            showToast('AI optimization complete. Cognitive peak windows updated!', 'success');
        } catch {
            showToast('Schedule compilation failed.', 'danger');
        } finally {
            btn.innerHTML = `<i class="fa-solid fa-wand-magic-sparkles"></i> Re-Optimize`;
            btn.disabled = false;
        }
    }, 1200);
}

// --- Dynamic Rendering: 4. Skills Recommender AI ---
async function generateAISkills() {
    const input = document.getElementById('career-goal');
    const goalVal = input.value.trim();
    
    if (!goalVal) {
        showToast('Please type in a career goal/role first.', 'warning');
        return;
    }
    
    const resultsContainer = document.getElementById('skills-results');
    
    // Set loading skeleton status
    resultsContainer.innerHTML = `
        <div class="empty-state" style="padding: 20px;">
            <i class="fa-solid fa-spinner fa-spin" style="font-size: 32px; color: var(--color-cyan); margin-bottom: 14px;"></i>
            <h4>Synthesizing Roadmaps...</h4>
            <p>Analyzing industry competencies and local academic prerequisites.</p>
        </div>
    `;
    
    // Simulate AI synthesis
    setTimeout(() => {
        let skills = [];
        
        // Custom smart answers based on query tags
        const q = goalVal.toLowerCase();
        if (q.includes('ai') || q.includes('machine') || q.includes('data')) {
            skills = [
                { name: "Supervised Learning Models", hours: 45, difficulty: "Intermediate", relevance: 98, resources: ["Andrew Ng Course", "Scikit-Learn Docs"] },
                { name: "Deep Neural Network Design (PyTorch)", hours: 60, difficulty: "Advanced", relevance: 95, resources: ["PyTorch Tutorials", "Fast.ai Practical Course"] },
                { name: "Vector Databases & LLM Integration", hours: 30, difficulty: "Advanced", relevance: 89, resources: ["Pinecone Handbook", "LangChain Notebooks"] },
                { name: "Dimensionality Reduction & PCA Analysis", hours: 25, difficulty: "Intermediate", relevance: 82, resources: ["Linear Algebra Lectures", "StatQuest Youtube"] }
            ];
        } else if (q.includes('devops') || q.includes('cloud') || q.includes('infrastructure')) {
            skills = [
                { name: "Docker Containerization & Orchestration", hours: 35, difficulty: "Intermediate", relevance: 96, resources: ["Docker Guide", "TechWorld with Nana"] },
                { name: "Kubernetes Pod Lifecycle & Deployments", hours: 55, difficulty: "Advanced", relevance: 92, resources: ["K8s Official Docs", "CKA Certification Path"] },
                { name: "Infrastructure as Code (Terraform)", hours: 40, difficulty: "Advanced", relevance: 88, resources: ["Terraform Up & Running", "HashiCorp Learn"] },
                { name: "CI/CD Pipeline Construction (GitHub Actions)", hours: 20, difficulty: "Easy", relevance: 85, resources: ["Git Automation Guide", "FreeCodeCamp Devops"] }
            ];
        } else if (q.includes('react') || q.includes('frontend') || q.includes('fullstack') || q.includes('web')) {
            skills = [
                { name: "State Architecture (Redux & React Query)", hours: 30, difficulty: "Intermediate", relevance: 95, resources: ["Redux Toolkit Docs", "Kent C. Dodds Guides"] },
                { name: "TypeScript Type Safety & Interfaces", hours: 25, difficulty: "Intermediate", relevance: 92, resources: ["TypeScript Deep Dive", "TS Playground"] },
                { name: "Node.js REST API Architecture", hours: 40, difficulty: "Intermediate", relevance: 87, resources: ["Express.js Guide", "The Net Ninja Playlist"] },
                { name: "Database Query Optimization (SQL)", hours: 30, difficulty: "Intermediate", relevance: 80, resources: ["SQL Performance Explained", "PostgreSQL Tutorial"] }
            ];
        } else {
            // Default General Software Engineering Track
            skills = [
                { name: "Algorithms & Complex Data Structures", hours: 60, difficulty: "Intermediate", relevance: 90, resources: ["LeetCode Study Plan", "MIT Introduction to Algorithms"] },
                { name: "Git Workflow & Repository Integrity", hours: 15, difficulty: "Easy", relevance: 88, resources: ["Pro Git Book", "GitHub Interactive Sandbox"] },
                { name: "System Design & Microservices Principles", hours: 50, difficulty: "Advanced", relevance: 85, resources: ["Designing Data-Intensive Apps", "ByteByteGo System Design"] }
            ];
        }
        
        // Render generated cards
        resultsContainer.innerHTML = '';
        skills.forEach((skill, index) => {
            const card = document.createElement('div');
            card.className = 'ai-skill-card';
            card.style.animationDelay = `${index * 0.1}s`;
            
            // Build resource chips
            const resourcesHTML = skill.resources.map(res => `
                <a href="#" class="resource-chip" onclick="window.open('https://www.google.com/search?q=${encodeURIComponent(res)}', '_blank'); return false;">
                    <i class="fa-solid fa-graduation-cap"></i> ${res}
                </a>
            `).join('');

            card.innerHTML = `
                <div class="ai-skill-card-top">
                    <div class="ai-skill-details">
                        <h4>${skill.name}</h4>
                        <div class="ai-skill-meta">
                            <span><i class="fa-solid fa-clock"></i> Est: ${skill.hours}h</span>
                            <span>•</span>
                            <span class="badge badge-accent">${skill.difficulty}</span>
                        </div>
                    </div>
                    <div class="relevance-score-container">
                        <span class="relevance-dot"></span>
                        <span class="relevance-val" style="font-weight: 700; color: var(--color-cyan);">${skill.relevance}% Rel</span>
                    </div>
                </div>
                <div class="resources-list">
                    ${resourcesHTML}
                </div>
                <div class="ai-skill-card-bottom">
                    <button class="btn btn-secondary btn-glow" style="padding: 6px 14px; font-size:12px;" onclick="trackSkill('${skill.name}', '${goalVal}')">
                        <i class="fa-solid fa-plus"></i> Track Skill
                    </button>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
        
        showToast('Personalized learning roadmap compiled successfully.', 'success');
        
    }, 1500);
}

async function trackSkill(name, goal) {
    // Check if already tracking
    if (state.targetSkills.some(s => s.name === name)) {
        showToast(`Already tracking ${name}!`, 'warning');
        return;
    }
    
    const newSkill = await requestAPI('/skills/targets', 'POST', { name, progress: 0, goal });
    state.targetSkills.push(newSkill);
    renderTargetSkills();
    updateGlobalStats();
    showToast(`Added '${name}' to target skills.`, 'success');
}

function renderTargetSkills() {
    const list = document.getElementById('target-skills-list');
    list.innerHTML = '';
    
    document.getElementById('target-skills-count').textContent = `${state.targetSkills.length} Tracked`;
    
    if (state.targetSkills.length === 0) {
        list.innerHTML = `<p style="padding: 10px; text-align: center; color: var(--text-muted); font-size:13px;">No skill targets added yet. Use AI generator to register skills.</p>`;
        return;
    }
    
    state.targetSkills.forEach(skill => {
        const item = document.createElement('div');
        item.className = 'target-skill-item glass-panel';
        item.innerHTML = `
            <div class="target-skill-header">
                <div class="target-skill-info">
                    <span class="target-skill-title">${skill.name}</span>
                    <p style="font-size:11px; color: var(--text-muted)">Mapped to: ${skill.goal || 'General Software Engineering'}</p>
                </div>
                <button class="btn-remove-skill" onclick="removeTargetSkill('${skill.id}')" title="Remove Tracked Skill">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
            <div class="skill-progress-bar-container">
                <div class="progress-header">
                    <span>Mastery Progress</span>
                    <span>${skill.progress}%</span>
                </div>
                <div class="progress-track">
                    <div class="progress-fill" style="width: ${skill.progress}%"></div>
                </div>
                <div style="display:flex; justify-content: flex-end; margin-top: 6px;">
                    <button class="btn-increment-progress" onclick="incrementSkillProgress('${skill.id}', ${skill.progress})">
                        <i class="fa-solid fa-plus"></i> Increment Progress
                    </button>
                </div>
            </div>
        `;
        list.appendChild(item);
    });
}

async function incrementSkillProgress(id, currentProgress) {
    const newProgress = Math.min(100, currentProgress + 10);
    await requestAPI(`/skills/targets/${id}`, 'PUT', { progress: newProgress });
    
    state.targetSkills = state.targetSkills.map(s => s.id === id ? { ...s, progress: newProgress } : s);
    renderTargetSkills();
    showToast('Progress updated!', 'success');
}

async function removeTargetSkill(id) {
    if (confirm('Stop tracking this target skill?')) {
        await requestAPI(`/skills/targets/${id}`, 'DELETE');
        state.targetSkills = state.targetSkills.filter(s => s.id !== id);
        renderTargetSkills();
        updateGlobalStats();
        showToast('Removed skill target.', 'info');
    }
}

// --- Dynamic Rendering: 5. Dashboard Overview Quick Peeks ---
function renderQuickSchedulePeek(scheduleItems) {
    const container = document.getElementById('quick-schedule');
    container.innerHTML = '';
    
    // Peak first 3 items
    const peakItems = scheduleItems.slice(0, 3);
    
    peakItems.forEach(item => {
        const row = document.createElement('div');
        row.className = 'quick-schedule-item';
        row.innerHTML = `
            <div class="quick-schedule-time">${item.time.split(' - ')[0]}</div>
            <div class="quick-schedule-info">
                <h4>${item.title}</h4>
                <p>${item.desc}</p>
            </div>
        `;
        container.appendChild(row);
    });
}

function renderQuickTasksPeek() {
    const container = document.getElementById('quick-tasks');
    container.innerHTML = '';
    
    // Sort tasks: high priority first, then medium, then low, and only show unfinished ones
    const priorityWeight = { high: 3, medium: 2, low: 1 };
    const pendingTasks = state.tasks
        .filter(t => t.status !== 'completed')
        .sort((a, b) => priorityWeight[b.priority] - priorityWeight[a.priority])
        .slice(0, 3);
        
    if (pendingTasks.length === 0) {
        container.innerHTML = `<p style="padding: 10px; text-align: center; color: var(--text-muted); font-size:13px;">All tasks completed! Good job.</p>`;
        return;
    }
    
    pendingTasks.forEach(task => {
        const row = document.createElement('div');
        row.className = `quick-task-item ${task.priority}`;
        row.innerHTML = `
            <div>
                <span class="quick-task-title">${task.title}</span>
                <p class="quick-task-meta">${task.category.toUpperCase()} • Due: ${formatDate(task.due_date)}</p>
            </div>
            <span class="badge ${getPriorityBadgeClass(task.priority)}">${task.priority}</span>
        `;
        container.appendChild(row);
    });
}

// --- Charts Setup & Integration (Chart.js) ---
function initCharts() {
    // 1. GPA Progression Line Chart
    const ctxGpa = document.getElementById('gpaChart').getContext('2d');
    
    // Create violet/cyan gradient fills
    const gpaGrad = ctxGpa.createLinearGradient(0, 0, 0, 300);
    gpaGrad.addColorStop(0, 'rgba(123, 97, 255, 0.45)');
    gpaGrad.addColorStop(1, 'rgba(123, 97, 255, 0.0)');
    
    const chartConfigGpa = {
        type: 'line',
        data: {
            labels: [], // Populated dynamically
            datasets: [{
                label: 'GPA Equivalent',
                data: [], // Populated dynamically
                borderColor: 'rgba(123, 97, 255, 1)',
                borderWidth: 3,
                backgroundColor: gpaGrad,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(0, 240, 255, 1)',
                pointBorderColor: '#fff',
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(18, 18, 26, 0.95)',
                    titleFont: { family: 'Outfit', size: 14, weight: 'bold' },
                    bodyFont: { family: 'Outfit', size: 13 },
                    borderColor: 'rgba(255, 255, 255, 0.08)',
                    borderWidth: 1,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { family: 'Outfit', size: 11 } }
                },
                y: {
                    min: 0,
                    max: 4.0,
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { stepSize: 0.5, color: 'rgba(255, 255, 255, 0.5)', font: { family: 'Outfit', size: 11 } }
                }
            }
        }
    };
    gpaChartInstance = new Chart(ctxGpa, chartConfigGpa);
    
    // 2. Productivity Radar/Bar Chart
    const ctxProd = document.getElementById('productivityChart').getContext('2d');
    const prodGrad = ctxProd.createLinearGradient(0, 0, 0, 300);
    prodGrad.addColorStop(0, 'rgba(0, 240, 255, 0.8)');
    prodGrad.addColorStop(1, 'rgba(123, 97, 255, 0.4)');
    
    const chartConfigProd = {
        type: 'bar',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'Study Duration (Hours)',
                    data: [3.5, 4.0, 5.5, 2.0, 3.0, 6.0, 1.5], // Populated dynamically or defaulted
                    backgroundColor: prodGrad,
                    borderRadius: 8,
                    borderWidth: 0,
                    barThickness: 18
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(18, 18, 26, 0.95)',
                    titleFont: { family: 'Outfit' },
                    bodyFont: { family: 'Outfit' }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { family: 'Outfit' } }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.03)' },
                    ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { family: 'Outfit' } }
                }
            }
        }
    };
    productivityChartInstance = new Chart(ctxProd, chartConfigProd);
    
    updateCharts();
}

function updateCharts() {
    if (!gpaChartInstance || !productivityChartInstance) return;
    
    // Update GPA Progression Chart
    // Sort courses (excluding In-Progress) to make a progression line
    const completedCourses = state.courses
        .filter(c => c.grade !== 'IP')
        .slice(-6); // Last 6 courses
        
    if (completedCourses.length > 0) {
        gpaChartInstance.data.labels = completedCourses.map(c => c.code);
        gpaChartInstance.data.datasets[0].data = completedCourses.map(c => c.gpa);
    } else {
        // Fallback placeholder data if empty
        gpaChartInstance.data.labels = ['Sem 1', 'Sem 2', 'Sem 3'];
        gpaChartInstance.data.datasets[0].data = [3.5, 3.8, 3.85];
    }
    gpaChartInstance.update();
    
    // Update Productivity patterns chart based on routine log history
    const weekdayDurations = [0, 0, 0, 0, 0, 0, 0]; // Mon-Sun cumulative study minutes
    
    state.routineLogs.forEach(log => {
        const d = new Date(log.date);
        let dayIndex = d.getDay() - 1; // getDay: 0 is Sun, 1 is Mon...
        if (dayIndex < 0) dayIndex = 6; // Shift Sun to end
        
        if (dayIndex >= 0 && dayIndex <= 6) {
            weekdayDurations[dayIndex] += Number(log.duration);
        }
    });
    
    // Convert to hours
    const weekdayHours = weekdayDurations.map(m => Number((m / 60).toFixed(1)));
    
    // Use fallback mock values if no routine log events exist
    const hasActiveData = weekdayHours.some(h => h > 0);
    productivityChartInstance.data.datasets[0].data = hasActiveData ? weekdayHours : [2.5, 3.5, 4.0, 1.5, 3.0, 5.0, 2.0];
    productivityChartInstance.update();
}

// --- Forms Submission Handling ---
function initForms() {
    // 1. Course Registration
    const courseForm = document.getElementById('course-form');
    courseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const code = document.getElementById('course-code').value.trim().toUpperCase();
        const name = document.getElementById('course-name').value.trim();
        const credits = Number(document.getElementById('course-credits').value);
        const grade = document.getElementById('course-grade').value;
        const gpa = Number(document.getElementById('course-gpa').value);
        
        const body = { code, name, credits, grade, gpa };
        const savedItem = await requestAPI('/courses', 'POST', body);
        
        state.courses.push(savedItem);
        renderCourses();
        updateGlobalStats();
        updateCharts();
        
        closeAllModals();
        courseForm.reset();
        showToast('New course registered successfully.', 'success');
    });

    // Automatically update GPA equivalents based on letter grade selection to help user
    const gradeSelect = document.getElementById('course-grade');
    const gpaInput = document.getElementById('course-gpa');
    
    gradeSelect.addEventListener('change', () => {
        const gradeMap = {
            'A+': 4.00, 'A': 4.00, 'A-': 3.70, 'B+': 3.30, 'B': 3.00,
            'B-': 2.70, 'C+': 2.30, 'C': 2.00, 'D': 1.00, 'F': 0.00, 'IP': 4.00
        };
        gpaInput.value = gradeMap[gradeSelect.value].toFixed(2);
    });

    // 2. Task Registration
    const taskForm = document.getElementById('task-form');
    taskForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const title = document.getElementById('task-title').value.trim();
        const description = document.getElementById('task-desc').value.trim();
        const priority = document.getElementById('task-priority').value;
        const category = document.getElementById('task-category').value;
        const due_date = document.getElementById('task-due').value;
        const status = document.getElementById('task-status').value;
        
        const body = { title, description, priority, category, due_date, status };
        const savedItem = await requestAPI('/tasks', 'POST', body);
        
        state.tasks.push(savedItem);
        renderTasks();
        updateGlobalStats();
        
        closeAllModals();
        taskForm.reset();
        showToast('New task added successfully.', 'success');
    });

    // Set today as default due date
    document.getElementById('task-due').value = getFutureDate(0);

    // 3. Routine Log Registration
    const routineForm = document.getElementById('routine-form');
    routineForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const activity = document.getElementById('routine-activity').value.trim();
        const duration = Number(document.getElementById('routine-duration').value);
        const productivity = Number(document.getElementById('routine-productivity').value);
        const date = document.getElementById('routine-date').value;
        const category = document.getElementById('routine-category').value;
        
        const body = { activity, duration, productivity, date, category };
        const savedItem = await requestAPI('/routine', 'POST', body);
        
        state.routineLogs.push(savedItem);
        renderRoutineLogs();
        updateGlobalStats();
        updateCharts();
        
        routineForm.reset();
        document.getElementById('routine-date').value = getFutureDate(0);
        showToast('Activity logged successfully.', 'success');
    });
    
    // Set default routine log date to today
    document.getElementById('routine-date').value = getFutureDate(0);
}

// --- Universal Modals Handler ---
function initModals() {
    // Open course modal
    document.getElementById('add-course-btn').addEventListener('click', () => {
        openModal('course-modal');
    });

    // Open task modal
    document.getElementById('add-task-btn').addEventListener('click', () => {
        openModal('task-modal');
    });

    // Close buttons
    document.querySelectorAll('.btn-close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            closeAllModals();
        });
    });

    // Click outside overlay to close
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeAllModals();
            }
        });
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

function closeAllModals() {
    document.querySelectorAll('.modal-overlay').forEach(modal => {
        modal.classList.remove('active');
    });
}

// --- Custom Toast Alert Utility ---
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconClass = 'fa-circle-info';
    if (type === 'success') iconClass = 'fa-circle-check';
    if (type === 'warning') iconClass = 'fa-triangle-exclamation';
    if (type === 'danger') iconClass = 'fa-circle-exclamation';
    
    toast.innerHTML = `
        <span class="toast-icon"><i class="fa-solid ${iconClass}"></i></span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()"><i class="fa-solid fa-xmark"></i></button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(10px) scale(0.9)';
            setTimeout(() => toast.remove(), 350);
        }
    }, 4000);
}
