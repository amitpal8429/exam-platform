from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import datetime
import shutil

app = Flask(__name__)

# ===== CONFIGURATION =====
RECORDINGS_DIR = "recordings"
QUESTIONS_FILE = "questions.json"
BACKUP_DIR = "question_backups"
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# ===== SESSION STORAGE =====
sessions = {}


# ===== DYNAMIC QUESTIONS LOADER =====
def load_questions():
    """Load questions from JSON file or create default"""
    if os.path.exists(QUESTIONS_FILE):
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        default = [
  {
    "id": 1,
    "question": "A 3-month-old infant presents with generalized xerosis, severe pruritus, recurrent Staphylococcus aureus skin infections, and markedly elevated total IgE. Whole-exome sequencing demonstrates a heterozygous loss-of-function mutation in FLG. Which immunologic mechanism most directly links the genetic defect to food allergy development?",
    "type": "mcq",
    "options": [
      "Enhanced IL-17 production by γδ T cells causing neutrophilic inflammation",
      "Epicutaneous allergen penetration inducing thymic stromal lymphopoietin (TSLP)-mediated Th2 sensitization",
      "Increased IFN-γ signaling causing keratinocyte apoptosis",
      "Deficiency of complement C3 leading to impaired opsonization"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 2,
    "question": "Which of the following histopathological findings best distinguishes acute atopic dermatitis from chronic atopic dermatitis?",
    "type": "mcq",
    "options": [
      "Regular psoriasiform epidermal hyperplasia",
      "Prominent spongiosis with intraepidermal vesiculation",
      "Hypergranulosis with wedge-shaped hyperkeratosis",
      "Full-thickness epidermal dysplasia"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 3,
    "question": "A neonate develops superficial flaccid bullae on the trunk and perineum. Nikolsky sign is positive. Mucous membranes are spared. Histopathology demonstrates a subcorneal split. Which toxin is responsible?",
    "type": "mcq",
    "options": [
      "TSST-1",
      "Exfoliative toxin A targeting desmoglein-1",
      "Alpha toxin",
      "Panton-Valentine leukocidin"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 4,
    "question": "An 8-year-old child develops widespread guttate papules two weeks after streptococcal pharyngitis. Which immunologic pathway has the strongest evidence for disease pathogenesis?",
    "type": "mcq",
    "options": [
      "IL-5 eosinophilic pathway",
      "IL-17/IL-23 axis",
      "IL-10 regulatory pathway",
      "Type I interferon pathway"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 5,
    "question": "Which dermoscopic finding is considered most characteristic of tinea capitis caused by Trichophyton tonsurans?",
    "type": "mcq",
    "options": [
      "Blue-white veil",
      "Arborizing vessels",
      "Corkscrew hairs and comma hairs",
      "Milky-red globules"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 6,
    "question": "A 7-year-old immunocompromised child develops painful hemorrhagic vesicles with fever. PCR confirms disseminated varicella-zoster virus infection. Which antiviral has the strongest evidence as first-line therapy?",
    "type": "mcq",
    "options": [
      "Oral famciclovir",
      "Intravenous acyclovir",
      "Oral valacyclovir only",
      "Topical cidofovir"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 7,
    "question": "A child presents with multiple café-au-lait macules, axillary freckling, Lisch nodules and a plexiform neurofibroma. Which mutation is responsible?",
    "type": "mcq",
    "options": [
      "PTCH1",
      "NF1",
      "TSC2",
      "GNAS"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 8,
    "question": "A newborn has generalized blistering immediately after birth. Immunofluorescence mapping localizes the cleavage plane within the lamina lucida. Which diagnosis is most likely?",
    "type": "mcq",
    "options": [
      "Epidermolysis bullosa simplex",
      "Junctional epidermolysis bullosa",
      "Dystrophic epidermolysis bullosa",
      "Bullous congenital ichthyosiform erythroderma"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 9,
    "question": "Which pediatric biologic selectively blocks IL-4 receptor α, thereby inhibiting both IL-4 and IL-13 signaling?",
    "type": "mcq",
    "options": [
      "Secukinumab",
      "Dupilumab",
      "Adalimumab",
      "Ustekinumab"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 10,
    "question": "A 4-year-old develops extensive impetigo unresponsive to oral cephalexin. Culture demonstrates community-associated MRSA. Which oral antibiotic is generally the most appropriate empiric alternative (assuming local susceptibility)?",
    "type": "mcq",
    "options": [
      "Penicillin V",
      "Dicloxacillin",
      "Clindamycin",
      "Cefixime"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 11,
    "question": "Which congenital vascular anomaly carries the greatest risk of association with PHACE syndrome?",
    "type": "mcq",
    "options": [
      "Small focal scalp hemangioma",
      "Large segmental facial infantile hemangioma",
      "Venous lake",
      "Pyogenic granuloma"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 12,
    "question": "A child with juvenile dermatomyositis develops painful ulcerative skin lesions despite corticosteroids. Persistent elevation of which autoantibody is most strongly associated with severe cutaneous vasculopathy?",
    "type": "mcq",
    "options": [
      "Anti-MDA5",
      "Anti-dsDNA",
      "Anti-Sm",
      "Anti-centromere"
    ],
    "correct": 0,
    "marks": 1
  },
  {
    "id": 13,
    "question": "Which biopsy technique provides the greatest diagnostic yield for suspected leukocytoclastic vasculitis?",
    "type": "mcq",
    "options": [
      "Shave biopsy of an ulcer",
      "Punch biopsy of a fresh lesion (<24 hours)",
      "Curettage",
      "Excisional biopsy of a healed lesion"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 14,
    "question": "A child receiving oral propranolol for infantile hemangioma develops lethargy and seizures after prolonged fasting. The most likely mechanism is:",
    "type": "mcq",
    "options": [
      "Hyperinsulinemia",
      "Masking of hypoglycemia with impaired glycogenolysis",
      "Hyponatremia",
      "Hyperkalemia"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 15,
    "question": "Which of the following represents the strongest indication for immediate admission to a pediatric intensive care or burn unit?",
    "type": "mcq",
    "options": [
      "Localized bullous impetigo",
      "Stevens–Johnson syndrome involving 15% body surface area with mucosal involvement",
      "Molluscum contagiosum",
      "Stable localized epidermolysis bullosa simplex"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 16,
    "question": "A randomized controlled trial comparing two topical agents for pediatric eczema reports: Relative Risk = 0.72, 95% Confidence Interval = 0.55–0.94, p = 0.018. Which interpretation is MOST accurate?",
    "type": "mcq",
    "options": [
      "The treatment significantly reduces risk because the confidence interval excludes 1.",
      "The study is statistically insignificant because RR is below 1.",
      "The p-value proves clinical superiority.",
      "Confidence intervals cannot determine significance."
    ],
    "correct": 0,
    "marks": 1
  },
  {
    "id": 17,
    "question": "A 13-year-old girl with vitiligo refuses to attend school because classmates bully her regarding her appearance. Which intervention is supported by current pediatric dermatology principles as part of comprehensive management?",
    "type": "mcq",
    "options": [
      "Delay psychosocial intervention until repigmentation occurs.",
      "Recommend school withdrawal.",
      "Integrate dermatologic treatment with psychological assessment, family counseling, and school-based support.",
      "Begin systemic corticosteroids solely to improve self-esteem."
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 18,
    "question": "A 2-year-old girl presents with persistent periorificial dermatitis, alopecia, chronic diarrhea, and irritability. Serum zinc is markedly reduced. Which transporter defect is responsible for the inherited form of this disorder?",
    "type": "mcq",
    "options": [
      "ATP7A",
      "ATP7B",
      "SLC39A4",
      "ABCA12"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 19,
    "question": "A 6-year-old boy with recurrent blistering over trauma-prone areas develops progressive mitten deformities of both hands. Genetic analysis most likely demonstrates mutation in:",
    "type": "mcq",
    "options": [
      "KRT14",
      "COL7A1",
      "LAMA3",
      "FLG"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 20,
    "question": "A newborn develops diffuse erythroderma with collodion membrane at birth. Electron microscopy reveals absent lamellar granules. Which diagnosis is most likely?",
    "type": "mcq",
    "options": [
      "Harlequin ichthyosis",
      "Lamellar ichthyosis",
      "Epidermolysis bullosa simplex",
      "Incontinentia pigmenti"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 21,
    "question": "A child with severe atopic dermatitis has persistent eosinophilia despite biologic therapy. Which cytokine is primarily responsible for eosinophil maturation in bone marrow?",
    "type": "mcq",
    "options": [
      "IL-5",
      "IL-12",
      "IL-18",
      "IL-27"
    ],
    "correct": 0,
    "marks": 1
  },
  {
    "id": 22,
    "question": "A neonate presents with diffuse pustules that rupture easily, leaving hyperpigmented macules with collarettes of scale. Wright stain demonstrates abundant neutrophils without eosinophils. The diagnosis is:",
    "type": "mcq",
    "options": [
      "Erythema toxicum neonatorum",
      "Transient neonatal pustular melanosis",
      "Neonatal candidiasis",
      "Bullous impetigo"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 23,
    "question": "A child receiving methotrexate for severe psoriasis develops painful oral ulcerations and pancytopenia. Which intervention should be administered immediately?",
    "type": "mcq",
    "options": [
      "Vitamin K",
      "Leucovorin rescue",
      "Pyridoxine",
      "Intravenous immunoglobulin"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 24,
    "question": "Which dermoscopic feature is most characteristic of psoriasis?",
    "type": "mcq",
    "options": [
      "Arborizing vessels",
      "Uniform dotted vessels over a light-red background with diffuse white scales",
      "Blue-gray globules",
      "Peripheral streaks"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 25,
    "question": "A 9-year-old immunocompromised child develops rapidly progressive black eschar involving the nasal ala. Which fungal pathogen should be suspected first?",
    "type": "mcq",
    "options": [
      "Candida albicans",
      "Aspergillus fumigatus",
      "Rhizopus species",
      "Trichophyton rubrum"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 26,
    "question": "A child with recurrent skin abscesses has absent neutrophil oxidative burst on flow cytometry (DHR test). Which dermatologic diagnosis is most commonly associated?",
    "type": "mcq",
    "options": [
      "Chronic granulomatous disease",
      "Hyper-IgM syndrome",
      "Wiskott-Aldrich syndrome",
      "Leukocyte adhesion deficiency"
    ],
    "correct": 0,
    "marks": 1
  },
  {
    "id": 27,
    "question": "Which congenital melanocytic nevus carries the greatest lifetime risk for melanoma?",
    "type": "mcq",
    "options": [
      "Small (<1.5 cm)",
      "Medium (1.5–20 cm)",
      "Giant (>40 cm projected adult size)",
      "Junctional nevus"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 28,
    "question": "A child with suspected juvenile dermatomyositis undergoes MRI. Which finding best reflects active muscle inflammation?",
    "type": "mcq",
    "options": [
      "Fatty replacement only",
      "T1 hypointensity without edema",
      "T2/STIR hyperintense muscle edema",
      "Muscle calcification only"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 29,
    "question": "Which topical corticosteroid has the highest potency?",
    "type": "mcq",
    "options": [
      "Hydrocortisone 1%",
      "Desonide 0.05%",
      "Clobetasol propionate 0.05%",
      "Fluocinolone acetonide 0.01%"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 30,
    "question": "A 15-year-old girl develops painful dusky macules, oral erosions, conjunctivitis, and epidermal detachment involving 18% body surface area after beginning lamotrigine. The diagnosis is:",
    "type": "mcq",
    "options": [
      "Bullous pemphigoid",
      "Staphylococcal scalded skin syndrome",
      "Stevens–Johnson syndrome/TEN overlap",
      "Pemphigus vulgaris"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 31,
    "question": "Which histopathologic feature is characteristic of lichen planus?",
    "type": "mcq",
    "options": [
      "Suprabasal clefting",
      "Saw-tooth acanthosis with band-like lymphocytic infiltrate",
      "Subcorneal pustules",
      "Basket-weave orthokeratosis"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 32,
    "question": "Which laser demonstrates the greatest efficacy for pediatric port-wine stains?",
    "type": "mcq",
    "options": [
      "CO₂ laser",
      "Pulsed dye laser (595 nm)",
      "Nd:YAG laser alone",
      "Alexandrite laser"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 33,
    "question": "A randomized trial reports: Relative Risk = 0.62, Absolute Risk Reduction = 10%. What is the correct Number Needed to Treat (NNT)?",
    "type": "mcq",
    "options": [
      "5",
      "8",
      "10",
      "20"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 34,
    "question": "A 14-year-old girl with severe psoriasis reports social withdrawal, declining academic performance, and suicidal ideation. According to current pediatric dermatology practice, the most appropriate next step is:",
    "type": "mcq",
    "options": [
      "Focus exclusively on systemic psoriasis treatment.",
      "Delay psychological assessment until skin lesions improve.",
      "Initiate multidisciplinary management including urgent mental health evaluation while optimizing dermatologic therapy.",
      "Reassure the family that psychiatric symptoms usually resolve spontaneously."
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 35,
    "question": "A full-term neonate is born encased in a taut, shiny membrane that fissures over the first 48 hours. There is marked ectropion and eclabium, but no blistering. Genetic testing is most likely to identify a mutation in:",
    "type": "mcq",
    "options": [
      "ABCA12",
      "COL7A1",
      "KRT14",
      "SPINK5"
    ],
    "correct": 0,
    "marks": 1
  },
  {
    "id": 36,
    "question": "A 6-year-old boy presents with generalized erythroderma, bamboo hair (trichorrhexis invaginata), recurrent bacterial infections, and severe atopy. Which syndrome is the most likely diagnosis?",
    "type": "mcq",
    "options": [
      "Omenn syndrome",
      "Hyper-IgE syndrome",
      "Netherton syndrome",
      "Wiskott-Aldrich syndrome"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 37,
    "question": "A child with recurrent herpes simplex virus infection undergoes evaluation. Which primary immunodeficiency most commonly predisposes to severe cutaneous HSV infections?",
    "type": "mcq",
    "options": [
      "Chronic granulomatous disease",
      "Severe combined immunodeficiency (SCID)",
      "Hereditary angioedema",
      "Selective IgA deficiency"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 38,
    "question": "Which of the following is the strongest indication for performing a direct immunofluorescence (DIF) biopsy in a child?",
    "type": "mcq",
    "options": [
      "Molluscum contagiosum",
      "Bullous impetigo",
      "Autoimmune blistering disease",
      "Verruca vulgaris"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 39,
    "question": "A 5-year-old presents with extensive crusted scabies. Microscopy demonstrates numerous mites. Which factor most strongly predisposes children to crusted scabies?",
    "type": "mcq",
    "options": [
      "Atopic dermatitis alone",
      "Immunosuppression or impaired cell-mediated immunity",
      "Iron deficiency anemia",
      "Vitamin D deficiency"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 40,
    "question": "Which immunologic pathway is predominantly responsible for the pathogenesis of alopecia areata in children?",
    "type": "mcq",
    "options": [
      "Th2-mediated eosinophilic inflammation",
      "Cytotoxic CD8+ T-cell attack on the hair follicle with IFN-γ signaling",
      "Immune-complex deposition",
      "Mast-cell degranulation"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 41,
    "question": "A child receiving long-term topical corticosteroids develops linear striae and telangiectasia. The primary pathogenic mechanism is:",
    "type": "mcq",
    "options": [
      "Increased fibroblast proliferation",
      "Collagen degradation and dermal atrophy",
      "Increased melanocyte activity",
      "Excess elastin production"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 42,
    "question": "A 12-year-old girl with localized scleroderma (morphea) develops progressive joint contractures despite topical therapy. The most appropriate next treatment is:",
    "type": "mcq",
    "options": [
      "Oral acyclovir",
      "Methotrexate with systemic corticosteroids",
      "Oral isotretinoin",
      "Topical mupirocin"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 43,
    "question": "A child presents with extensive port-wine stain involving the ophthalmic (V1) distribution of the trigeminal nerve. Which associated syndrome should be suspected?",
    "type": "mcq",
    "options": [
      "PHACE syndrome",
      "Sturge-Weber syndrome",
      "Proteus syndrome",
      "Klippel-Trénaunay syndrome"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 44,
    "question": "Which histologic finding is most characteristic of Langerhans cell histiocytosis?",
    "type": "mcq",
    "options": [
      "Touton giant cells",
      "Birbeck granules on electron microscopy",
      "Russell bodies",
      "Civatte bodies"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 45,
    "question": "A child develops diffuse desquamation, fever, hypotension, and multiorgan dysfunction caused by toxin-producing Staphylococcus aureus. Which superantigen is classically implicated?",
    "type": "mcq",
    "options": [
      "Exfoliative toxin B",
      "Toxic Shock Syndrome Toxin-1 (TSST-1)",
      "Alpha toxin",
      "Enterotoxin G"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 46,
    "question": "Which topical calcineurin inhibitor is approved for moderate-to-severe pediatric atopic dermatitis and does not cause skin atrophy?",
    "type": "mcq",
    "options": [
      "Hydrocortisone",
      "Tacrolimus ointment",
      "Betamethasone valerate",
      "Clobetasol propionate"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 47,
    "question": "A multicenter pediatric trial evaluating a new biologic for severe atopic dermatitis randomizes participants to biologic or placebo. This design is best classified as:",
    "type": "mcq",
    "options": [
      "Cross-sectional study",
      "Case-control study",
      "Randomized controlled trial",
      "Ecological study"
    ],
    "correct": 2,
    "marks": 1
  },
  {
    "id": 48,
    "question": "A 15-year-old with severe acne develops sudden fever, painful ulcerative nodules, polyarthralgia, leukocytosis, and elevated inflammatory markers shortly after initiating isotretinoin. Which diagnosis is most likely?",
    "type": "mcq",
    "options": [
      "Acne conglobata",
      "Acne fulminans",
      "Rosacea fulminans",
      "Gram-negative folliculitis"
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 49,
    "question": "A dermatologist is providing teledermatology services to families in remote communities. Which practice is most appropriate for maintaining high-quality pediatric care?",
    "type": "mcq",
    "options": [
      "Diagnose all pigmented lesions exclusively from photographs.",
      "Use secure platforms, obtain informed consent, document image quality, and arrange in-person evaluation when diagnostic uncertainty or procedural management exists.",
      "Avoid communication with primary care physicians.",
      "Prescribe systemic immunosuppressants without laboratory monitoring."
    ],
    "correct": 1,
    "marks": 1
  },
  {
    "id": 50,
    "question": "A 14-year-old with severe psoriasis reports bullying, anxiety, treatment non-adherence, and declining quality of life. Which management strategy is most consistent with contemporary pediatric dermatology practice?",
    "type": "mcq",
    "options": [
      "Focus solely on clearing the skin because psychosocial symptoms usually resolve automatically.",
      "Refer only to psychiatry and discontinue dermatologic treatment.",
      "Integrate evidence-based dermatologic therapy with psychological screening, family counseling, school support, and shared decision-making.",
      "Delay treatment until adulthood because biologics are contraindicated in adolescents."
    ],
    "correct": 2,
    "marks": 1
  }
]
        save_questions(default)
        return default


def save_questions(questions):
    """Save questions to JSON file with backup"""
    if os.path.exists(QUESTIONS_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"questions_{timestamp}.json")
        shutil.copy(QUESTIONS_FILE, backup_path)
        print(f"✅ Backup created: {backup_path}")

    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)
    print(f"✅ Questions saved: {QUESTIONS_FILE}")


QUESTIONS = load_questions()


# ===== ROUTES =====

@app.route("/")
def home():
    return """
    <html>
    <body style='font-family:sans-serif;padding:40px;background:#0d0f18;color:#e2e8f0'>
        <h2>📚 Exam Platform Running</h2>
        <p style='margin-top:12px'>
            <a href='/admin' style='color:#7c6ff7'>Admin Panel</a> | 
            <a href='/admin/questions' style='color:#7c6ff7'>Manage Questions</a> |
            <a href='/admin/reports' style='color:#7c6ff7'>Reports</a> |
            <a href='/generate_links' style='color:#7c6ff7'>Generate Links</a>
        </p>
        <p style='color:#475569;margin-top:20px'>
            Students: <a href='/exam/student_name' style='color:#7c6ff7'>/exam/student_name</a>
        </p>
    </body>
    </html>
    """


@app.route("/exam/<student_id>")
def exam(student_id):
    """Student exam page"""
    current_questions = load_questions()
    if student_id not in sessions:
        sessions[student_id] = {
            "student_id": student_id,
            "start_time": datetime.datetime.now().isoformat(),
            "answers": {},
            "submitted": False,
            "video_saved": False,
            "video_file": None,
            "alerts": [],
            "chunk_count": 0
        }
        print(f"[NEW] Student joined: {student_id}")
    return render_template("exam.html",
                           student_id=student_id,
                           questions=current_questions,
                           submitted=sessions[student_id]["submitted"])


@app.route("/generate_links")
def generate_links():
    """Generate exam links for students"""
    public_url = os.environ.get("RENDER_EXTERNAL_URL", os.environ.get("PUBLIC_URL", "http://localhost:5000"))

    if os.path.exists("public_url.txt") and public_url == "http://localhost:5000":
        with open("public_url.txt", "r") as f:
            public_url = f.read().strip()

    students = ["rahul", "priya", "amit", "sneha", "vikram", "neha", "raj", "anita"]
    links = []
    for student in students:
        links.append({
            "name": student,
            "url": f"{public_url}/exam/{student}"
        })

    return render_template("generate_links.html", links=links, public_url=public_url)


@app.route("/upload_chunk/<student_id>", methods=["POST"])
def upload_chunk(student_id):
    """Receive video chunks during exam"""
    if "chunk" not in request.files:
        return jsonify({"error": "No chunk"}), 400

    chunk_file = request.files["chunk"]
    chunk_num = request.form.get("chunk_num", "0")
    chunk_type = request.form.get("type", "cam")

    student_dir = os.path.join(RECORDINGS_DIR, student_id)
    os.makedirs(student_dir, exist_ok=True)

    filename = f"{chunk_type}_chunk_{str(chunk_num).zfill(3)}.webm"
    chunk_file.save(os.path.join(student_dir, filename))

    if student_id in sessions:
        sessions[student_id]["chunk_count"] = int(chunk_num)

    print(f"[CHUNK] {student_id} -> {filename}")
    return jsonify({"status": "saved", "chunk": chunk_num})


@app.route("/upload_video/<student_id>", methods=["POST"])
def upload_video(student_id):
    """Receive final video on submission"""
    if "video" not in request.files:
        return jsonify({"error": "No video"}), 400

    video_file = request.files["video"]
    video_type = request.form.get("type", "cam")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{student_id}_{video_type}_{timestamp}_FINAL.webm"
    filepath = os.path.join(RECORDINGS_DIR, filename)
    video_file.save(filepath)
    size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 2)

    print(f"[VIDEO] Saved: {filepath} ({size_mb} MB)")

    if student_id in sessions:
        sessions[student_id]["video_saved"] = True
        sessions[student_id]["video_file"] = filename

        log_path = os.path.join(RECORDINGS_DIR, f"{student_id}_{timestamp}_log.json")
        with open(log_path, "w", encoding='utf-8') as f:
            json.dump({
                "student": student_id,
                "start_time": sessions[student_id]["start_time"],
                "end_time": datetime.datetime.now().isoformat(),
                "video_file": filename,
                "alerts": sessions[student_id]["alerts"],
                "answers": sessions[student_id]["answers"]
            }, f, indent=2, ensure_ascii=False)

    return jsonify({"status": "saved", "file": filename, "size_mb": size_mb})


@app.route("/save_alert/<student_id>", methods=["POST"])
def save_alert(student_id):
    """Save proctoring alerts"""
    data = request.get_json()
    if student_id in sessions:
        sessions[student_id]["alerts"].append({
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "alert": data.get("alert", "")
        })
        print(f"[ALERT] {student_id}: {data.get('alert')}")
    return jsonify({"status": "ok"})


@app.route("/submit/<student_id>", methods=["POST"])
def submit(student_id):
    """Submit exam answers"""
    data = request.get_json()
    if student_id in sessions and not sessions[student_id]["submitted"]:
        sessions[student_id]["answers"] = data.get("answers", {})
        sessions[student_id]["submitted"] = True
        sessions[student_id]["end_time"] = datetime.datetime.now().isoformat()

        ans_path = os.path.join(RECORDINGS_DIR, f"{student_id}_answers.json")
        with open(ans_path, "w", encoding='utf-8') as f:
            json.dump(sessions[student_id], f, indent=2, ensure_ascii=False)
        print(f"[SUBMIT] {student_id} submitted")

    return jsonify({"status": "submitted"})


@app.route("/admin")
def admin():
    """Admin dashboard"""
    files = []
    for fname in os.listdir(RECORDINGS_DIR):
        fpath = os.path.join(RECORDINGS_DIR, fname)
        if os.path.isfile(fpath):
            files.append({
                "name": fname,
                "size_mb": round(os.path.getsize(fpath) / (1024 * 1024), 2)
            })

    folders = []
    for fname in os.listdir(RECORDINGS_DIR):
        fpath = os.path.join(RECORDINGS_DIR, fname)
        if os.path.isdir(fpath):
            folders.append({
                "name": fname,
                "chunks": len(os.listdir(fpath))
            })

    files.sort(key=lambda x: x["name"], reverse=True)

    public_url = os.environ.get("RENDER_EXTERNAL_URL", os.environ.get("PUBLIC_URL", "http://localhost:5000"))
    if os.path.exists("public_url.txt") and public_url == "http://localhost:5000":
        with open("public_url.txt", "r") as f:
            public_url = f.read().strip()

    return render_template("admin.html", sessions=sessions, files=files, folders=folders, public_url=public_url)


@app.route("/admin/questions", methods=['GET', 'POST'])
def manage_questions():
    """Question management page"""
    global QUESTIONS

    if request.method == 'POST':
        try:
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                data = request.get_json()
                if 'questions' in data:
                    new_questions = data['questions']
                    save_questions(new_questions)
                    QUESTIONS = new_questions
                    return jsonify({"status": "success", "message": "Questions updated!"})

            new_questions = []
            question_count = int(request.form.get('question_count', 0))

            for i in range(question_count):
                q_type = request.form.get(f'q_{i}_type')
                q_data = {
                    "id": i + 1,
                    "question": request.form.get(f'q_{i}_question'),
                    "type": q_type,
                    "marks": int(request.form.get(f'q_{i}_marks', 5))
                }

                if q_type == 'mcq':
                    options = [
                        request.form.get(f'q_{i}_opt_0', ''),
                        request.form.get(f'q_{i}_opt_1', ''),
                        request.form.get(f'q_{i}_opt_2', ''),
                        request.form.get(f'q_{i}_opt_3', '')
                    ]
                    q_data["options"] = options
                    q_data["correct"] = int(request.form.get(f'q_{i}_correct', 0))

                new_questions.append(q_data)

            save_questions(new_questions)
            QUESTIONS = new_questions

            return jsonify({"status": "success", "message": "Questions updated!"})

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    current_questions = load_questions()
    return render_template("manage_questions.html", questions=current_questions)


@app.route("/admin/reports")
def reports():
    """Generate reports with correct answers count"""
    report_data = []
    questions = load_questions()  # Load questions for correct answer checking

    for fname in os.listdir(RECORDINGS_DIR):
        if fname.endswith("_answers.json"):
            fpath = os.path.join(RECORDINGS_DIR, fname)
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Calculate correct answers
                answers = data.get('answers', {})
                correct_count = 0

                for q in questions:
                    qid = str(q['id'])
                    if qid in answers:
                        if q.get('type') == 'mcq':
                            if q.get('correct') == answers[qid]:
                                correct_count += 1
                        else:
                            # For text questions, count if answered
                            if answers[qid] and str(answers[qid]).strip():
                                correct_count += 1

                report_data.append({
                    'student': data.get('student_id', 'Unknown'),
                    'submitted': data.get('submitted', False),
                    'answers': len(answers),
                    'correct': correct_count,
                    'alerts': len(data.get('alerts', [])),
                    'start_time': data.get('start_time', ''),
                    'end_time': data.get('end_time', '')
                })

    return render_template("reports.html", reports=report_data)


@app.route("/recordings/<path:filename>")
def download_file(filename):
    """Download recording files"""
    return send_from_directory(RECORDINGS_DIR, filename, as_attachment=True)


@app.route("/api/questions", methods=['GET'])
def api_get_questions():
    """API endpoint to get current questions"""
    return jsonify(load_questions())


@app.route("/api/upload_questions", methods=['POST'])
def api_upload_questions():
    """API endpoint to upload questions via JSON"""
    global QUESTIONS

    try:
        data = request.get_json()
        if 'questions' not in data:
            return jsonify({"error": "Missing 'questions' field"}), 400

        new_questions = data['questions']
        save_questions(new_questions)
        QUESTIONS = new_questions
        return jsonify({"status": "success", "message": "Questions updated!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ===== API ROUTE FOR DAILY UPLOAD =====
@app.route("/api/daily_upload", methods=['POST'])
def api_daily_upload():
    """API endpoint to run daily upload"""
    global QUESTIONS

    try:
        from daily_upload import daily_upload
        questions = daily_upload()
        QUESTIONS = questions
        return jsonify({
            "status": "success",
            "message": f"Uploaded {len(questions)} questions for today",
            "questions": questions
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


# ===== MAIN =====
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  📚 EXAM PLATFORM STARTING")
    print("=" * 60)

    is_render = os.environ.get("RENDER", False)

    if is_render:
        print("  🚀 Running on Render.com")
        port = int(os.environ.get("PORT", 5000))
        print(f"  🌐 Port: {port}")
    else:
        print("  💻 Running locally on http://localhost:5000")
        print("  📝 To deploy on Render, push to GitHub and connect")

    print("\n" + "=" * 60)
    print("  💡 TIPS:")
    print("  • Press CTRL+C to stop the server")
    print("  • Use /generate_links to create student links")
    print("  • All recordings are saved locally in 'recordings/'")
    print("=" * 60 + "\n")

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=not is_render, host="0.0.0.0", port=port, threaded=True)