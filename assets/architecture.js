/**
 * EduPulse AI — Interactive Architecture Showcase Logic
 * Handles layer inspection, pipeline stepper, and interactive What-If simulation.
 */

document.addEventListener('DOMContentLoaded', () => {
    initLayerInspector();
    initPipelineStepper();
    initWhatIfSimulator();
    initScrollSpy();
});

/* ==========================================================================
   1. ARCHITECTURE LAYER INSPECTOR
   ========================================================================== */
const layerData = {
    layer1: {
        title: "Layer 1: Data Sources & Ingestion Points",
        meta: "Raw Student Academic, Behavioral & Engagement Ingestion",
        description: "Captures multi-dimensional student performance and interaction signals from campus administrative and digital learning environments.",
        inputs: "Student course records, LMS portal activity logs, lecture attendance scanner logs, assignment submission timestamps, and student wellness self-reports.",
        outputs: "Tabular raw student profile records containing 8 core features plus demographic identifiers (Student ID, Name, Major, Grade Level, Tuition Status).",
        file: "data/students_1200.csv & generate_data.py",
        functions: "generate_student_dataset(), load_student_data()",
        notes: "Project uses 1,200 synthetic student records with correlated Gaussian distributions for hackathon demonstration. Future roadmap includes LMS LTI integration (Canvas/Blackboard)."
    },
    layer2: {
        title: "Layer 2: Data Processing & Feature Engineering",
        meta: "src/data_loader.py — Validation, Normalization & Filtering",
        description: "Cleans, validates, caches, and filters student cohorts. Extracts structured numerical feature vectors required for model inference.",
        inputs: "CSV dataset stream, user-applied filter criteria (Major, Grade Level, Risk Tier, Search Query).",
        outputs: "Filtered Pandas DataFrame, standardized 8-feature numerical vectors (FEATURE_COLS), and aggregated cohort-level KPIs.",
        file: "src/data_loader.py",
        functions: "load_student_data(), get_filtered_students(), get_cohort_kpis()",
        notes: "Implements Streamlit @st.cache_data for instant in-memory retrieval and cohort metric aggregation."
    },
    layer3: {
        title: "Layer 3: Machine Learning Risk Classification",
        meta: "models/risk_model.pkl — 120-Tree Random Forest Classifier",
        description: "Executes supervised multi-class risk classification. Employs 120 balanced decision trees trained on an 80/20 stratified split to achieve 90.0% evaluation accuracy.",
        inputs: "8 aligned features: attendance_rate, gpa, assignment_completion_rate, midterm_score, study_hours_per_week, lms_engagement_score, participation_score, stress_level.",
        outputs: "Predicted risk tier (High / Medium / Low), calibrated class probability vectors, 0-100 Student Success Score, and feature Z-score impact rankings.",
        file: "src/model_utils.py & train_model.py",
        functions: "load_model(), predict_student_risk(), explain_student_indicators()",
        notes: "Model artifact is pickled with Joblib and cryptographically verified at load time using SHA-256 checksum verification."
    },
    layer4: {
        title: "Layer 4: Analytics & Decision Support Engine",
        meta: "app.py & src/recommendations.py — Multi-Mode Advisory Platform",
        description: "Translates raw model probabilities into actionable educational intelligence, visual dashboards, and prescriptive support roadmaps.",
        inputs: "Inference outputs, student profile attributes, institutional risk thresholds, and scenario adjustment parameters.",
        outputs: "Interactive Plotly visual analytics, prioritized academic recovery actions, real-time What-If sensitivity simulations, and sanitized CSV data exports.",
        file: "app.py & src/recommendations.py",
        functions: "generate_recommendations(), render_overview_tab(), render_what_if_simulator()",
        notes: "Provides 6 integrated modules: Cohort Overview, Risk Predictor, Deep Dive Profile, AI Recommendations, What-If Simulator, and Data Explorer."
    },
    layer5: {
        title: "Layer 5: Institutional Outcomes & Student Interventions",
        meta: "Advisory Success, Early Retention & Student Recovery",
        description: "Delivers targeted outcomes to academic stakeholders: proactive advisor outreach, tutoring assignments, wellness referrals, and early retention.",
        inputs: "Prioritized recommendations, student risk flags, and advisor case assignments.",
        outputs: "Measurable student retention, early identification before midterm failure, targeted study pods, and personalized recovery roadmaps.",
        file: "src/recommendations.py",
        functions: "generate_recommendations(student_data, risk_pred)",
        notes: "Categorizes interventions into Emergency Intervention (High Priority), Proactive Support (Medium Priority), Tutoring, Attendance Contracts, and Career Placement."
    }
};

function initLayerInspector() {
    const layerCards = document.querySelectorAll('.arch-layer-card');
    const inspectorPanel = document.getElementById('layerInspector');
    const titleEl = document.getElementById('inspectTitle');
    const metaEl = document.getElementById('inspectMeta');
    const descEl = document.getElementById('inspectDesc');
    const inputsEl = document.getElementById('inspectInputs');
    const outputsEl = document.getElementById('inspectOutputs');
    const fileEl = document.getElementById('inspectFile');
    const funcsEl = document.getElementById('inspectFuncs');
    const notesEl = document.getElementById('inspectNotes');

    layerCards.forEach(card => {
        card.addEventListener('click', () => {
            const layerKey = card.dataset.layer;
            const data = layerData[layerKey];
            if (!data) return;

            // Highlight active card
            layerCards.forEach(c => c.classList.remove('active-layer'));
            card.classList.add('active-layer');

            // Populate inspector
            titleEl.textContent = data.title;
            metaEl.textContent = data.meta;
            descEl.textContent = data.description;
            inputsEl.textContent = data.inputs;
            outputsEl.textContent = data.outputs;
            fileEl.textContent = data.file;
            funcsEl.textContent = data.functions;
            notesEl.textContent = data.notes;

            inspectorPanel.classList.add('active');
            inspectorPanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
    });
}

/* ==========================================================================
   2. AI MODEL & DATA PIPELINE STEPPER
   ========================================================================== */
const pipelineSteps = [
    {
        title: "Step 1: Student Dataset Ingestion",
        icon: "📁",
        desc: "Ingests structured academic and engagement records from data/students_1200.csv containing 1,200 records with 14 attributes including GPA, attendance, assignment completion, midterm score, study hours, LMS activity, stress level, and tuition status.",
        badge: "data/students_1200.csv (1,200 Rows × 14 Columns)",
        file: "generate_data.py"
    },
    {
        title: "Step 2: Data Cleaning & Feature Preparation",
        icon: "⚙️",
        desc: "Extracts the 8 numerical predictor features (FEATURE_COLS), performs data validation and type verification, and calculates cohort statistics (mean, std, min, max) for normalization and benchmarking.",
        badge: "FEATURE_COLS = ['attendance', 'gpa', 'assignment', 'midterm', 'study_hours', 'lms', 'participation', 'stress']",
        file: "src/data_loader.py"
    },
    {
        title: "Step 3: Model Inference & Probability Calculation",
        icon: "🧠",
        desc: "Passes the student feature vector to the pre-loaded Scikit-Learn RandomForestClassifier (120 estimators, max_depth 10). Executes predict() and predict_proba() to derive empirical probability distribution across High, Medium, and Low risk classes.",
        badge: "clf.predict_proba(input_df) → [P(High), P(Medium), P(Low)]",
        file: "src/model_utils.py (predict_student_risk)"
    },
    {
        title: "Step 4: Risk Tier & Success Score Computation",
        icon: "🎯",
        desc: "Maps probabilities to risk classification (High, Medium, Low) and computes the 0-100 Student Success Score: Success Score = max(0, min(100, 100 - (high_risk_prob * 0.85 + medium_risk_prob * 0.35))). Computes feature Z-scores against cohort means.",
        badge: "Success Score Formula + Feature Z-Score Impact Badges",
        file: "src/model_utils.py"
    },
    {
        title: "Step 5: Context-Aware Recommendation Engine",
        icon: "🛠️",
        desc: "Evaluates individual student metrics against defined academic recovery thresholds: Attendance < 75% triggers attendance contracts, GPA < 2.5 triggers peer tutoring, Midterm < 60% triggers remedial review, and High Risk triggers mandatory advisor intake.",
        badge: "generate_recommendations(student_data, risk_pred)",
        file: "src/recommendations.py"
    },
    {
        title: "Step 6: Interactive Analytics & What-If Simulation",
        icon: "📊",
        desc: "Presents insights on the Streamlit dashboard across 6 interactive operational modes with Plotly visualizations, cohort KPI summaries, student search, and a real-time What-If scenario planning simulator.",
        badge: "Streamlit UI + Plotly Express / Graph Objects",
        file: "app.py"
    }
];

function initPipelineStepper() {
    const nodes = document.querySelectorAll('.pipeline-step-node');
    const iconEl = document.getElementById('pipelineDetailIcon');
    const titleEl = document.getElementById('pipelineDetailTitle');
    const descEl = document.getElementById('pipelineDetailDesc');
    const badgeEl = document.getElementById('pipelineDetailBadge');

    nodes.forEach((node, index) => {
        node.addEventListener('click', () => {
            nodes.forEach(n => n.classList.remove('active-node'));
            node.classList.add('active-node');

            const step = pipelineSteps[index];
            if (step) {
                iconEl.textContent = step.icon;
                titleEl.textContent = step.title;
                descEl.textContent = step.desc;
                badgeEl.textContent = step.badge;
            }
        });
    });
}

/* ==========================================================================
   3. WHAT-IF INTERACTIVE MINI-SIMULATOR
   Demonstrates real-time scenario planning matching EduPulse AI formulas
   ========================================================================== */
function initWhatIfSimulator() {
    const attendanceSlider = document.getElementById('simAttendance');
    const gpaSlider = document.getElementById('simGpa');
    const assignmentSlider = document.getElementById('simAssignment');
    const studyHoursSlider = document.getElementById('simStudyHours');

    const valAttendance = document.getElementById('valAttendance');
    const valGpa = document.getElementById('valGpa');
    const valAssignment = document.getElementById('valAssignment');
    const valStudyHours = document.getElementById('valStudyHours');

    const riskBadge = document.getElementById('simRiskBadge');
    const successVal = document.getElementById('simSuccessVal');
    const progressFill = document.getElementById('simProgressFill');

    function updateSimulation() {
        const att = parseFloat(attendanceSlider.value);
        const gpa = parseFloat(gpaSlider.value);
        const assign = parseFloat(assignmentSlider.value);
        const study = parseFloat(studyHoursSlider.value);

        // Update labels
        valAttendance.textContent = att + '%';
        valGpa.textContent = gpa.toFixed(2);
        valAssignment.textContent = assign + '%';
        valStudyHours.textContent = study + ' hrs';

        // Calculate synthetic risk index mirroring generate_data.py & model_utils.py
        // Risk score index: 0 (lowest risk) to 100 (highest risk)
        const riskIndex = (
            (100 - att) * 0.28 +
            ((4.0 - gpa) / 4.0 * 100) * 0.28 +
            (100 - assign) * 0.22 +
            ((35 - Math.min(35, study)) / 35 * 100) * 0.22
        );

        // Success score (0 to 100 scale)
        const successScore = Math.max(0, Math.min(100, Math.round((100 - riskIndex) * 10) / 10));

        // Assign risk tier
        let riskTier = "Low";
        let badgeClass = "risk-badge-low";

        if (riskIndex > 48) {
            riskTier = "High Risk";
            badgeClass = "risk-badge-high";
        } else if (riskIndex > 28) {
            riskTier = "Medium Risk";
            badgeClass = "risk-badge-med";
        } else {
            riskTier = "Low Risk";
            badgeClass = "risk-badge-low";
        }

        // Update UI
        riskBadge.textContent = riskTier;
        riskBadge.className = 'sim-risk-badge ' + badgeClass;
        successVal.textContent = successScore + ' / 100';
        progressFill.style.width = successScore + '%';

        if (successScore >= 70) {
            progressFill.style.background = 'linear-gradient(90deg, #10B981, #5FF2A5)';
        } else if (successScore >= 50) {
            progressFill.style.background = 'linear-gradient(90deg, #F59E0B, #FBBF24)';
        } else {
            progressFill.style.background = 'linear-gradient(90deg, #EF4444, #F87171)';
        }
    }

    [attendanceSlider, gpaSlider, assignmentSlider, studyHoursSlider].forEach(slider => {
        if (slider) {
            slider.addEventListener('input', updateSimulation);
        }
    });

    updateSimulation();
}

/* ==========================================================================
   4. ACTIVE NAVIGATION SCROLL SPY
   ========================================================================== */
function initScrollSpy() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');

    window.addEventListener('scroll', () => {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            const sectionHeight = section.offsetHeight;
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
}
