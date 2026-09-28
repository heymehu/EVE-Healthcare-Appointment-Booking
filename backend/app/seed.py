"""Seed hospitals, diagnostic centres and clinics for EVE Healthcare.

Safe to run multiple times: centres are matched by name and tests by
(centre, test name), so re-running only refreshes the stored values.
"""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.diagnostic_centre import DiagnosticCentre
from app.models.test import DiagnosticTest

CATEGORIES = [
    "Cardiology",
    "Blood Test",
    "MRI Scan",
    "CT Scan",
    "Ultrasound",
    "X-Ray",
    "Neurology",
    "Full Body Checkup",
]

CENTRE_FIELDS = (
    "location",
    "description",
    "image_url",
    "rating",
    "review_count",
    "centre_type",
    "address",
    "city",
    "pincode",
    "phone",
    "accreditation",
    "panels",
    "open_time",
    "is_open_now",
    "starting_price",
)


def centre(
    name: str,
    centre_type: str,
    address: str,
    city: str,
    pincode: str,
    description: str,
    image_url: str,
    rating: str,
    review_count: int,
    tests: list[tuple],
    accreditation: str = "NABL Accredited",
    panels: str = "CGHS, ECHS, Corporate Empanelment",
    phone: str = "011-4000 1000",
    open_time: str = "7:00 AM - 9:00 PM",
    is_open_now: bool = True,
) -> dict:
    return {
        "name": name,
        "centre_type": centre_type,
        "address": address,
        "city": city,
        "pincode": pincode,
        "location": f"{city}, {'Delhi NCR' if city in ('New Delhi', 'Noida', 'Gurugram', 'Ghaziabad', 'Faridabad') else city}",
        "description": description,
        "image_url": image_url,
        "rating": Decimal(rating),
        "review_count": review_count,
        "accreditation": accreditation,
        "panels": panels,
        "phone": phone,
        "open_time": open_time,
        "is_open_now": is_open_now,
        "tests": tests,
    }


CENTRES = [
    centre(
        name="Apollo Hospitals Delhi",
        centre_type="Hospital",
        address="Sarita Vihar, Mathura Road, Okhla Phase II",
        city="New Delhi",
        pincode="110076",
        description=(
            "Multi-specialty 700-bed hospital with a dedicated cardiac sciences block, NABL accredited "
            "pathology lab, 3T MRI suite and 128-slice CT scan with same-day digital reporting."
        ),
        image_url="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80",
        rating="4.7",
        review_count=1842,
        phone="011-2987 1000",
        tests=[
            ("Complete Blood Count (CBC)", "Blood Test", "Measures red cells, white cells, haemoglobin and platelets.", Decimal("350.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart disease risk.", Decimal("650.00")),
            ("Cardiac Markers Panel (Trop-I, BNP)", "Cardiology", "High-sensitivity cardiac biomarkers for chest pain triage.", Decimal("2400.00")),
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("400.00")),
            ("2D Echocardiography (ECHO)", "Cardiology", "Ultrasound imaging of heart valves and chamber structure.", Decimal("1900.00")),
            ("Treadmill Stress Test (TMT)", "Cardiology", "Exercise electrocardiogram testing cardiac endurance.", Decimal("1600.00")),
            ("Thyroid Profile (T3, T4, TSH)", "Blood Test", "Evaluates thyroid gland function.", Decimal("750.00")),
            ("Brain MRI (3T HD Scan)", "MRI Scan", "High-definition magnetic resonance imaging of brain tissue.", Decimal("4800.00")),
            ("Chest X-Ray Digital", "X-Ray", "Digital radiograph of lungs, ribs and cardiac silhouette.", Decimal("450.00")),
            ("Abdominal Ultrasound", "Ultrasound", "Sonography of the liver, gall bladder and kidneys.", Decimal("1300.00")),
            ("Corporate Master Health Checkup", "Full Body Checkup", "85 parameters covering cardiac, lipid, thyroid and metabolic profile.", Decimal("5499.00")),
        ],
    ),
    centre(
        name="Fortis Hospital Gurugram",
        centre_type="Hospital",
        address="Sector 44, Institutional Area, Gurugram",
        city="Gurugram",
        pincode="122002",
        description=(
            "JCI and NABL accredited tertiary hospital with 24/7 emergency cardiac testing, colour doppler "
            "ultrasound, digital mammography and a full body executive screening suite."
        ),
        image_url="https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1200&q=80",
        rating="4.8",
        review_count=1560,
        phone="0124-492 8888",
        tests=[
            ("HbA1c (Glycated Haemoglobin)", "Blood Test", "Measures average blood sugar over the past 3 months.", Decimal("500.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("700.00")),
            ("24-Hour Holter Monitoring", "Cardiology", "Continuous ECG tracking to detect intermittent arrhythmias.", Decimal("3000.00")),
            ("Dobutamine Stress Echo", "Cardiology", "Pharmacological stress echocardiogram for cardiac function.", Decimal("3400.00")),
            ("Carotid Colour Doppler Ultrasound", "Ultrasound", "Duplex doppler study of the neck carotid arteries.", Decimal("2600.00")),
            ("Digital Mammography (Bilateral)", "X-Ray", "Low-dose digital breast radiology screening.", Decimal("1800.00")),
            ("Whole Body PET-CT Scan", "CT Scan", "Advanced molecular imaging for metabolic and oncology scans.", Decimal("18500.00")),
            ("Nerve Conduction Study (NCS)", "Neurology", "Measures speed of electrical signals in peripheral nerves.", Decimal("2400.00")),
            ("Executive Cardiac + Lipid Screening", "Cardiology", "Combined ECG, ECHO, lipid and troponin cardiac screen.", Decimal("4200.00")),
        ],
    ),
    centre(
        name="Max Hospital Noida",
        centre_type="Hospital",
        address="Sector 18, Noida, Gautam Buddh Nagar",
        city="Noida",
        pincode="201301",
        description=(
            "Super-specialty hospital known for interventional cardiology with a cath lab, 64-slice CT coronary "
            "angiography, lumbar spine MRI and specialised haematology pathology."
        ),
        image_url="https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80",
        rating="4.9",
        review_count=1310,
        phone="0120-419 8888",
        tests=[
            ("Coronary CT Angiography", "Cardiology", "Non-invasive 3D imaging of the heart coronary arteries.", Decimal("8900.00")),
            ("High Sensitivity CRP (hs-CRP)", "Cardiology", "Inflammatory cardiac marker for cardiovascular risk.", Decimal("950.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Screening for anaemia, infection and immunity.", Decimal("320.00")),
            ("Haemoglobinopathy Profile", "Blood Test", "Detects thalassaemia and sickle cell traits.", Decimal("2200.00")),
            ("Spine MRI (Lumbar / Cervical)", "MRI Scan", "MRI imaging of spinal cord, discs and vertebrae.", Decimal("5100.00")),
            ("High Resolution CT Chest (HRCT)", "CT Scan", "Fine-slice CT scan for detailed lung screening.", Decimal("4100.00")),
            ("Electocardiography (ECG) with Interpretation", "Cardiology", "Resting ECG with cardiologist sign-off.", Decimal("400.00")),
            ("Executive Health Package", "Full Body Checkup", "Comprehensive screening for adults with cardiac markers.", Decimal("4999.00")),
        ],
    ),
    centre(
        name="Narayana Super Speciality Hospital",
        centre_type="Hospital",
        address="Sector 12, Institutional Area, Noida",
        city="Noida",
        pincode="201301",
        description=(
            "Cardiac-first super-speciality hospital with a paediatric congenital heart centre, advanced echo lab, "
            "bone densitometry (DEXA) and round-the-clock trauma imaging."
        ),
        image_url="https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=1200&q=80",
        rating="4.6",
        review_count=980,
        phone="0120-452 8888",
        tests=[
            ("Cardiac Troponin I Test", "Cardiology", "High-sensitivity cardiac marker for myocardial health.", Decimal("1200.00")),
            ("2D Echocardiography with Colour Doppler", "Cardiology", "Structural and flow assessment of the heart.", Decimal("2000.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia, infection and immunity.", Decimal("300.00")),
            ("Liver Function Test (LFT)", "Blood Test", "Assesses liver enzymes, bilirubin and proteins.", Decimal("650.00")),
            ("DEXA Bone Densitometry Scan", "X-Ray", "Low-dose DXA scan for osteoporosis screening.", Decimal("3200.00")),
            ("Whole Body MRI Screening", "MRI Scan", "Full-body MRI for tumour and systemic screening.", Decimal("22000.00")),
            ("EEG Brain Mapping", "Neurology", "Electroencephalogram monitoring of brain electrical activity.", Decimal("1900.00")),
            ("Senior Citizen Cardiac Screening", "Full Body Checkup", "Age-specific heart and metabolic screening package.", Decimal("3999.00")),
        ],
    ),
    centre(
        name="Sir Ganga Ram Hospital",
        centre_type="Hospital",
        address="Rajinder Nagar, New Delhi",
        city="New Delhi",
        pincode="110060",
        description=(
            "NABL and NABH accredited multi-speciality hospital with one of the busiest cardiac surgery units in "
            "Delhi, an advanced imaging centre and fully automated pathology."
        ),
        image_url="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1200&q=80",
        rating="4.7",
        review_count=2104,
        phone="011-2575 0000",
        tests=[
            ("Coronary Artery Calcium Score CT", "Cardiology", "Low-dose CT calcium scoring for heart attack risk.", Decimal("7500.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("680.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine blood screening for anaemia and infection.", Decimal("310.00")),
            ("Vitamin D3 & B12 Combo", "Blood Test", "Essential vitamin status analysis.", Decimal("1600.00")),
            ("Cardiac MRI", "MRI Scan", "MRI assessment of heart structure, myocardium and viability.", Decimal("12500.00")),
            ("Coronary CT Angiography", "CT Scan", "Non-invasive 3D imaging of coronary arteries.", Decimal("9200.00")),
            ("Bilateral Digital Mammography", "X-Ray", "Low-dose digital breast radiology screening.", Decimal("1900.00")),
            ("Arogya Cardiac Checkup", "Full Body Checkup", "Cardiac-focused preventive health package with ECG and ECHO.", Decimal("5999.00")),
        ],
    ),
    centre(
        name="BLK Super Speciality Hospital",
        centre_type="Hospital",
        address="Bakshi Bazar Road, Punjabi Bagh, New Delhi",
        city="New Delhi",
        pincode="110033",
        description=(
            "Tertiary care hospital with a high-volume cardiac centre, dedicated neuroscience block, PET-CT imaging "
            "and 24/7 stroke and trauma services."
        ),
        image_url="https://images.unsplash.com/photo-1516841273335-e39b37888115?auto=format&fit=crop&w=1200&q=80",
        rating="4.5",
        review_count=1167,
        phone="011-3067 3000",
        tests=[
            ("Cardiac MRI", "MRI Scan", "MRI assessment of heart structure and viability.", Decimal("13200.00")),
            ("Stress Test (TMT)", "Cardiology", "Exercise electrocardiogram testing cardiac endurance.", Decimal("1700.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and infection.", Decimal("330.00")),
            ("Kidney Function Test (KFT)", "Blood Test", "Evaluates creatinine, blood urea and electrolytes.", Decimal("600.00")),
            ("Whole Body PET-CT", "CT Scan", "Advanced molecular imaging for oncology staging.", Decimal("19500.00")),
            ("Carotid Doppler Ultrasound", "Ultrasound", "Duplex doppler study of the carotid arteries.", Decimal("2700.00")),
            ("EEG with Video Recording", "Neurology", "Long duration EEG for epilepsy and sleep disorders.", Decimal("4200.00")),
            ("Comprehensive Cardiac + Metabolic Panel", "Full Body Checkup", "Treadmill, lipid, sugar, thyroid and haemogram screening.", Decimal("5299.00")),
        ],
    ),
    centre(
        name="Medanta Super Specialty Hospital",
        centre_type="Hospital",
        address="Sector 17, Gurugram, Haryana",
        city="Gurugram",
        pincode="122003",
        description=(
            "Large multi-organ hospital with an advanced cardiac institute, electrophysiology lab, brain MRI suite "
            "and robotics-assisted imaging services."
        ),
        image_url="https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=1200&q=80",
        rating="4.8",
        review_count=1755,
        phone="0124-406 1000",
        tests=[
            ("Electrophysiology Study (EPS)", "Cardiology", "Catheter-based study to diagnose heart rhythm disorders.", Decimal("14500.00")),
            ("Transthoracic Echocardiography", "Cardiology", "Ultrasound imaging of heart valves and chambers.", Decimal("2100.00")),
            ("HbA1c (Glycated Haemoglobin)", "Blood Test", "Measures average blood sugar over the past 3 months.", Decimal("520.00")),
            ("Thyroid Profile (T3, T4, TSH)", "Blood Test", "Evaluates thyroid gland function.", Decimal("780.00")),
            ("Brain MRI with MR Angiography", "MRI Scan", "High-definition brain MRI with vessel imaging.", Decimal("7200.00")),
            ("CT Pulmonary Angiography", "CT Scan", "Imaging of pulmonary arteries for embolism and hypertension.", Decimal("8400.00")),
            ("Thyroid Ultrasound with FNAC", "Ultrasound", "Nodule imaging with guided fine needle aspiration.", Decimal("2200.00")),
            ("Nerve Conduction Study (NCS)", "Neurology", "Measures speed of electrical signals in peripheral nerves.", Decimal("2500.00")),
            ("Medi-Heart Executive Screening", "Full Body Checkup", "Cardiology, imaging and lab screening combined package.", Decimal("6499.00")),
        ],
    ),
    centre(
        name="Kokilaben Dhirubhai Ambani Hospital",
        centre_type="Hospital",
        address="Three Bungalows, Andheri West, Mumbai",
        city="Mumbai",
        pincode="400053",
        description=(
            "Tertiary hospital with a cardiac care tower, 3T MRI and PET-CT, advanced endoscopy and an in-house "
            "NABL accredited pathology laboratory."
        ),
        image_url="https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=1200&q=80",
        rating="4.8",
        review_count=1420,
        phone="022-2656 7777",
        panels="Corporate Empanelment",
        tests=[
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("420.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("720.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Screening for anaemia, infection and immunity.", Decimal("360.00")),
            ("Cardiac MRI", "MRI Scan", "MRI assessment of heart structure, myocardium and viability.", Decimal("12900.00")),
            ("Whole Body FDG PET-CT", "CT Scan", "Molecular imaging for oncology and infection.", Decimal("21000.00")),
            ("Interventional Cardiac CT Angiography", "CT Scan", "Non-invasive 3D coronary artery imaging.", Decimal("9500.00")),
            ("Full Body Master Health Checkup", "Full Body Checkup", "76 parameters including cardiac, lipid and metabolic panels.", Decimal("7499.00")),
        ],
    ),
    centre(
        name="Artemis Health Institute",
        centre_type="Hospital",
        address="Sector 51, Gurugram, Haryana",
        city="Gurugram",
        pincode="122001",
        description=(
            "Integrated hospital with a cardiac sciences institute, comprehensive radiology suite and preventive "
            "health screening programmes for corporate clients."
        ),
        image_url="https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=1200&q=80",
        rating="4.7",
        review_count=1233,
        phone="0124-451 8888",
        tests=[
            ("High Sensitivity Troponin-I", "Cardiology", "Ultra-sensitive cardiac injury marker.", Decimal("1400.00")),
            ("Stress Test (TMT)", "Cardiology", "Exercise electrocardiogram testing cardiac endurance.", Decimal("1750.00")),
            ("Iron Studies (Iron, TIBC, Ferritin)", "Blood Test", "Diagnoses iron deficiency and anaemia causes.", Decimal("1100.00")),
            ("Vitamin D3 & B12 Combo", "Blood Test", "Essential vitamin status analysis.", Decimal("1650.00")),
            ("Whole Body MRI", "MRI Scan", "Full-body MRI screening for systemic conditions.", Decimal("23000.00")),
            ("HRCT Chest", "CT Scan", "Fine-slice CT imaging for detailed lung screening.", Decimal("4300.00")),
            ("Obstetric Ultrasound", "Ultrasound", "Detailed pregnancy ultrasound imaging.", Decimal("1500.00")),
            ("Cardiac & Metabolic Screening", "Full Body Checkup", "ECG, ECHO, lipid, sugar and thyroid screening package.", Decimal("4799.00")),
        ],
    ),
    centre(
        name="PSRI Institute of Medical Sciences",
        centre_type="Hospital",
        address="Park View, Punjabi Bagh, New Delhi",
        city="New Delhi",
        pincode="110016",
        description=(
            "NABH accredited hospital with a dedicated cardiac unit, high-end imaging including 3T MRI and "
            "mammography, and a fully automated central pathology lab."
        ),
        image_url="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80",
        rating="4.6",
        review_count=903,
        phone="011-4566 0000",
        tests=[
            ("Cardiac Troponin I Test", "Cardiology", "High-sensitivity cardiac marker for myocardial health.", Decimal("1150.00")),
            ("24-Hour Holter Monitoring", "Cardiology", "Continuous ECG tracking to detect intermittent arrhythmias.", Decimal("3100.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and infection.", Decimal("315.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("690.00")),
            ("Bilateral Digital Mammography", "X-Ray", "Low-dose digital breast radiology screening.", Decimal("1750.00")),
            ("Kidney Joint MRI", "MRI Scan", "MRI evaluation of knee ligaments and cartilage.", Decimal("4500.00")),
            ("EEG Brain Mapping", "Neurology", "Electroencephalogram monitoring of brain electrical activity.", Decimal("1950.00")),
            ("Preventive Cardiac Screening", "Full Body Checkup", "Complete cardiac and lipid screening for adults.", Decimal("3599.00")),
        ],
    ),
    centre(
        name="Jaypee Hospital",
        centre_type="Hospital",
        address="Sector 18, Noida, Uttar Pradesh",
        city="Noida",
        pincode="201301",
        description=(
            "NABL and NABH accredited hospital with cardiac sciences, advanced MRI, digital radiology and a busy "
            "emergency and trauma imaging department."
        ),
        image_url="https://images.unsplash.com/photo-1586773860418-d37222d8fce3?auto=format&fit=crop&w=1200&q=80",
        rating="4.4",
        review_count=812,
        phone="0120-419 3333",
        tests=[
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("380.00")),
            ("2D Echocardiography (ECHO)", "Cardiology", "Ultrasound imaging of heart valves and chamber structure.", Decimal("1800.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Screening for anaemia, infection and immunity.", Decimal("290.00")),
            ("Fasting & PP Blood Sugar Combo", "Blood Test", "Plasma glucose check before and after meals.", Decimal("280.00")),
            ("CT Angiography (Cardiac)", "CT Scan", "Non-invasive 3D imaging of heart vessels.", Decimal("8600.00")),
            ("Whole Abdomen Ultrasound", "Ultrasound", "Ultrasound screening of abdominal organs.", Decimal("1250.00")),
            ("Brain MRI (3T HD Scan)", "MRI Scan", "High-definition magnetic resonance imaging of brain tissue.", Decimal("4600.00")),
            ("Basic Health Screening Package", "Full Body Checkup", "Essential haematology, lipid, sugar and thyroid screening.", Decimal("1999.00")),
        ],
    ),
    centre(
        name="Rainbow Children Hospital & Research Centre",
        centre_type="Hospital",
        address="Malviya Nagar, New Delhi",
        city="New Delhi",
        pincode="110017",
        description=(
            "Speciality hospital with paediatric and fetal medicine expertise offering fetal echocardiography, "
            "neonatal screening and paediatric imaging in a child-friendly environment."
        ),
        image_url="https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1200&q=80",
        rating="4.7",
        review_count=1067,
        phone="011-4058 8000",
        panels="CGHS, Corporate Empanelment",
        tests=[
            ("Fetal Echocardiography", "Cardiology", "Detailed ultrasound imaging of the foetal heart.", Decimal("3800.00")),
            ("Newborn Screening Panel", "Blood Test", "Heel-stick screening for metabolic and blood disorders.", Decimal("1900.00")),
            ("Paediatric ECG", "Cardiology", "Resting ECG adapted for infants and children.", Decimal("450.00")),
            ("Fetal MRI", "MRI Scan", "MRI imaging of the foetal brain and body.", Decimal("14500.00")),
            ("Paediatric Chest X-Ray", "X-Ray", "Digital radiograph for paediatric chest evaluation.", Decimal("420.00")),
            ("Whole Body Ultrasound", "Ultrasound", "Abdominal and soft tissue ultrasound screening.", Decimal("1600.00")),
            ("Child Growth & Development Screening", "Full Body Checkup", "Age-appropriate developmental and nutritional screening.", Decimal("2199.00")),
        ],
    ),
    centre(
        name="Amrita Institute of Medical Sciences",
        centre_type="Hospital",
        address="Sector 88, Faridabad, Haryana",
        city="Faridabad",
        pincode="121006",
        description=(
            "Tertiary care hospital with a cardiac sciences centre, high-end MRI and CT imaging, neuro diagnostics "
            "and a large NABL accredited central laboratory."
        ),
        image_url="https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80",
        rating="4.6",
        review_count=944,
        phone="0121-249 1000",
        tests=[
            ("Cardiac Catheterisation (Diagnostic)", "Cardiology", "Invasive coronary assessment by cardiac catheterisation.", Decimal("28000.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("640.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and infection.", Decimal("305.00")),
            ("Coagulation Profile", "Blood Test", "PT, aPTT and INR assessment of blood clotting.", Decimal("900.00")),
            ("Whole Body PET-CT", "CT Scan", "Molecular imaging for oncology and metabolic scans.", Decimal("17800.00")),
            ("Brain MRI (3T HD Scan)", "MRI Scan", "High-definition magnetic resonance imaging of brain tissue.", Decimal("4900.00")),
            ("Nerve Conduction Study (NCS)", "Neurology", "Measures speed of electrical signals in nerves.", Decimal("2350.00")),
            ("Cardiac Health Master Package", "Full Body Checkup", "ECG, ECHO, troponin, lipid and sugar screening.", Decimal("4499.00")),
        ],
    ),
    centre(
        name="Sterling Health Services",
        centre_type="Hospital",
        address="Sector 20, Rohini, New Delhi",
        city="New Delhi",
        pincode="110042",
        description=(
            "Neighbourhood hospital with emergency cardiac care, pathology, digital X-ray, ultrasound and an "
            "in-house pharmacy for quick outpatient diagnostics."
        ),
        image_url="https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=1200&q=80",
        rating="4.4",
        review_count=688,
        phone="011-4545 5555",
        open_time="8:00 AM - 8:00 PM",
        tests=[
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("350.00")),
            ("2D Echocardiography (ECHO)", "Cardiology", "Ultrasound imaging of heart valves and chambers.", Decimal("1700.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and infection.", Decimal("280.00")),
            ("Lipid Profile", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("600.00")),
            ("Chest X-Ray Digital", "X-Ray", "Digital radiograph of the chest.", Decimal("400.00")),
            ("Whole Abdomen Ultrasound", "Ultrasound", "Ultrasound screening of abdominal organs.", Decimal("1200.00")),
            ("Essential Health Checkup", "Full Body Checkup", "Haematology, lipid, sugar and thyroid screening package.", Decimal("1499.00")),
        ],
    ),
    centre(
        name="Metropolis Healthcare Diagnostics",
        centre_type="Diagnostic Center",
        address="Sector 18, Noida, Uttar Pradesh",
        city="Noida",
        pincode="201301",
        description=(
            "NABL and CAP accredited pathology chain with cardiac biomarkers, neuro diagnostics, immunoassay "
            "endocrinology and specialised metabolic test panels."
        ),
        image_url="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1200&q=80",
        rating="4.6",
        review_count=1288,
        phone="011-4055 6677",
        tests=[
            ("HbA1c (Glycated Haemoglobin)", "Blood Test", "Measures average blood sugar over the past 3 months.", Decimal("480.00")),
            ("Cardiac Troponin I Test", "Cardiology", "High-sensitivity cardiac marker for myocardial health.", Decimal("1050.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("560.00")),
            ("Liver Function Test (LFT)", "Blood Test", "Assesses liver enzymes, bilirubin and proteins.", Decimal("620.00")),
            ("Kidney Function Test (KFT)", "Blood Test", "Evaluates creatinine, blood urea and electrolytes.", Decimal("580.00")),
            ("Nerve Conduction Study (NCS)", "Neurology", "Measures speed of electrical signals in peripheral nerves.", Decimal("2200.00")),
            ("Thyroid Profile (T3, T4, TSH)", "Blood Test", "Evaluates thyroid gland function.", Decimal("720.00")),
            ("Cardiac Risk Complete Panel", "Cardiology", "Lipid, homocysteine, CRP and cardiac marker screening.", Decimal("2650.00")),
        ],
    ),
    centre(
        name="Dr. Lal PathLabs Diagnostic Centre",
        centre_type="Diagnostic Center",
        address="Okhla Phase II, New Delhi",
        city="New Delhi",
        pincode="110020",
        description=(
            "India's leading diagnostic network offering routine pathology, PET-CT imaging, digital radiology, "
            "ultrasound and full body health checkup packages."
        ),
        image_url="https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=1200&q=80",
        rating="4.8",
        review_count=2380,
        phone="011-4023 2020",
        tests=[
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia, infection and immunity.", Decimal("280.00")),
            ("Vitamin D3 & B12 Combo", "Blood Test", "Essential vitamin status analysis.", Decimal("1500.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("590.00")),
            ("Whole Body PET-CT Scan", "CT Scan", "Advanced molecular imaging for metabolic and oncology scans.", Decimal("16500.00")),
            ("Abdomen & Pelvis Ultrasound", "Ultrasound", "Ultrasound screening of abdominal organs.", Decimal("1250.00")),
            ("EEG Brain Mapping", "Neurology", "Electroencephalogram monitoring of brain electrical activity.", Decimal("1850.00")),
            ("Chest X-Ray Digital", "X-Ray", "Digital radiograph of the chest.", Decimal("420.00")),
            ("Full Body Master Health Checkup", "Full Body Checkup", "74 parameters including lipid, LFT, KFT and CBC.", Decimal("2499.00")),
        ],
    ),
    centre(
        name="Thyrocare Laboratories",
        centre_type="Diagnostic Center",
        address="Sector 10, Gurugram, Haryana",
        city="Gurugram",
        pincode="122002",
        description=(
            "Specialised diagnostic laboratory for fully automated thyroid, cardiac risk, diabetes, vitamin and "
            "hormone panels with home sample collection across NCR."
        ),
        image_url="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",
        rating="4.5",
        review_count=1576,
        phone="011-4066 8899",
        open_time="6:00 AM - 7:00 PM",
        tests=[
            ("Thyroid Profile (T3, T4, TSH)", "Blood Test", "Evaluates thyroid gland function.", Decimal("350.00")),
            ("Cardiac Risk Complete Profile", "Cardiology", "Lipid, homocysteine, CRP and cardiac marker screening.", Decimal("2100.00")),
            ("HbA1c (Glycated Haemoglobin)", "Blood Test", "Measures average blood sugar over the past 3 months.", Decimal("390.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and immunity.", Decimal("240.00")),
            ("Vitamin D3 (25-Hydroxy)", "Blood Test", "Vitamin D status analysis.", Decimal("600.00")),
            ("Diabetic Risk Plus Profile", "Blood Test", "HbA1c, insulin and microalbumin screening.", Decimal("1850.00")),
        ],
    ),
    centre(
        name="HealthOn Diagnostics",
        centre_type="Diagnostic Center",
        address="Aya Nagar, Mehrauli, New Delhi",
        city="New Delhi",
        pincode="110030",
        description=(
            "Bookable diagnostic centre offering radiology, cardiology, neuro diagnostics and pathology with "
            "same-day digital reports and home collection."
        ),
        image_url="https://images.unsplash.com/photo-1516549655169-df83a0774514?auto=format&fit=crop&w=1200&q=80",
        rating="4.4",
        review_count=742,
        phone="011-4004 9000",
        open_time="7:00 AM - 8:00 PM",
        tests=[
            ("2D Echocardiography (ECHO)", "Cardiology", "Ultrasound imaging of heart valves and chambers.", Decimal("1600.00")),
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("300.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and immunity.", Decimal("260.00")),
            ("Brain MRI (1.5T)", "MRI Scan", "High-definition magnetic resonance imaging of brain tissue.", Decimal("3400.00")),
            ("HRCT Chest", "CT Scan", "Fine-slice CT imaging for detailed lung screening.", Decimal("3200.00")),
            ("X-Ray Digital (Single View)", "X-Ray", "Low-dose digital radiograph for any body part.", Decimal("350.00")),
            ("Nerve Conduction Study (NCS)", "Neurology", "Measures speed of electrical signals in nerves.", Decimal("1800.00")),
            ("Basic Health Checkup", "Full Body Checkup", "Essential screening package for routine monitoring.", Decimal("1299.00")),
        ],
    ),
    centre(
        name="Redcliffe Diagnostics",
        centre_type="Diagnostic Center",
        address="Sector 14, Gurugram, Haryana",
        city="Gurugram",
        pincode="122001",
        description=(
            "Modern diagnostic centre with 3T MRI, low-dose CT, digital X-ray, ultrasound and a preventive health "
            "screening suite for corporate and family plans."
        ),
        image_url="https://images.unsplash.com/photo-1538108149393-fbbd81895907?auto=format&fit=crop&w=1200&q=80",
        rating="4.3",
        review_count=531,
        phone="0124-463 3000",
        open_time="8:00 AM - 8:00 PM",
        tests=[
            ("3T Whole Body MRI", "MRI Scan", "High-resolution full-body magnetic resonance imaging.", Decimal("13500.00")),
            ("HRCT Chest", "CT Scan", "Fine-slice CT imaging for detailed lung screening.", Decimal("3100.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and immunity.", Decimal("250.00")),
            ("Lipid Profile", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("550.00")),
            ("Whole Abdomen Ultrasound", "Ultrasound", "Ultrasound screening of abdominal organs.", Decimal("1150.00")),
            ("X-Ray Digital (Single View)", "X-Ray", "Low-dose digital radiograph for any body part.", Decimal("320.00")),
            ("Family Health Screening", "Full Body Checkup", "Preventive screening package for all family members.", Decimal("2999.00")),
        ],
    ),
    centre(
        name="SRL Diagnostics Centre",
        centre_type="Diagnostic Center",
        address="Sector 62, Noida, Uttar Pradesh",
        city="Noida",
        pincode="201309",
        description=(
            "Fully automated pathology and radiology centre with cardiac risk testing, digital imaging and "
            "comprehensive preventive health packages."
        ),
        image_url="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80",
        rating="4.4",
        review_count=865,
        phone="0120-456 6677",
        open_time="6:30 AM - 8:00 PM",
        tests=[
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and immunity.", Decimal("270.00")),
            ("Cardiac Risk Markers Panel", "Cardiology", "Homocysteine, hs-CRP and cardiac marker screening.", Decimal("1750.00")),
            ("HbA1c (Glycated Haemoglobin)", "Blood Test", "Measures average blood sugar over the past 3 months.", Decimal("420.00")),
            ("Liver Function Test (LFT)", "Blood Test", "Assesses liver enzymes, bilirubin and proteins.", Decimal("560.00")),
            ("Ultrasound Whole Abdomen", "Ultrasound", "Ultrasound screening of abdominal organs.", Decimal("1050.00")),
            ("Chest X-Ray Digital", "X-Ray", "Digital radiograph of the chest.", Decimal("360.00")),
            ("Full Body Health Checkup", "Full Body Checkup", "68 parameters of routine lab and imaging screening.", Decimal("1899.00")),
        ],
    ),
    centre(
        name="Apollo Clinic Heart Zone",
        centre_type="Clinic",
        address="B Block, Greater Kailash I, New Delhi",
        city="New Delhi",
        pincode="110048",
        description=(
            "Outpatient heart clinic offering consultations, ECG, echocardiography, TMT and ambulatory blood "
            "pressure monitoring with same-week appointments."
        ),
        image_url="https://images.unsplash.com/photo-1516841273335-e39b37888115?auto=format&fit=crop&w=1200&q=80",
        rating="4.5",
        review_count=612,
        phone="011-4100 5500",
        open_time="9:00 AM - 7:00 PM",
        tests=[
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("300.00")),
            ("2D Echocardiography (ECHO)", "Cardiology", "Ultrasound imaging of heart valves and chambers.", Decimal("1500.00")),
            ("Treadmill Stress Test (TMT)", "Cardiology", "Exercise electrocardiogram testing cardiac endurance.", Decimal("1400.00")),
            ("24-Hour Holter Monitoring", "Cardiology", "Continuous ECG tracking for intermittent arrhythmias.", Decimal("2500.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("620.00")),
            ("HbA1c (Glycated Haemoglobin)", "Blood Test", "Measures average blood sugar over the past 3 months.", Decimal("450.00")),
        ],
    ),
    centre(
        name="Max Clinic Cardiac Care",
        centre_type="Clinic",
        address="Connaught Place, New Delhi",
        city="New Delhi",
        pincode="110001",
        description=(
            "Preventive cardiology clinic focused on early heart disease detection through lipid profiling, ECG, "
            "ECG and lifestyle counselling."
        ),
        image_url="https://images.unsplash.com/photo-1631549916768-4119b2e5f926?auto=format&fit=crop&w=1200&q=80",
        rating="4.6",
        review_count=498,
        phone="011-4099 8888",
        open_time="9:00 AM - 7:00 PM",
        tests=[
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("700.00")),
            ("Cardiac Troponin I Test", "Cardiology", "High-sensitivity cardiac marker for myocardial health.", Decimal("1150.00")),
            ("12-Lead ECG", "Cardiology", "Rhythm and electrical activity of the heart.", Decimal("320.00")),
            ("High Sensitivity CRP (hs-CRP)", "Cardiology", "Inflammatory cardiac marker for cardiovascular risk.", Decimal("880.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and immunity.", Decimal("320.00")),
            ("Thyroid Profile (T3, T4, TSH)", "Blood Test", "Evaluates thyroid gland function.", Decimal("760.00")),
        ],
    ),
    centre(
        name="Neighbourhood Diagnostics & Blood Collection Point",
        centre_type="Clinic",
        address="Sector 50, Noida, Uttar Pradesh",
        city="Noida",
        pincode="201301",
        description=(
            "Community level clinic offering walk-in blood collection, quick turnaround haemograms and referral "
            "imaging at partner hospitals."
        ),
        image_url="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1200&q=80",
        rating="4.2",
        review_count=288,
        phone="0120-456 1000",
        open_time="7:00 AM - 8:00 PM",
        tests=[
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and infection.", Decimal("220.00")),
            ("Fasting & PP Blood Sugar Combo", "Blood Test", "Plasma glucose check before and after meals.", Decimal("200.00")),
            ("Lipid Profile", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("480.00")),
            ("Thyroid Profile (T3, T4, TSH)", "Blood Test", "Evaluates thyroid gland function.", Decimal("580.00")),
            ("Urine Routine Examination", "Blood Test", "Routine urine screening for kidney and infection markers.", Decimal("250.00")),
        ],
    ),
    centre(
        name="AIIMS Super Specialty Diagnostic Block",
        centre_type="Hospital",
        address="Ansari Road, New Delhi",
        city="New Delhi",
        pincode="110029",
        description=(
            "Tertiary academic hospital with advanced cardiac imaging, whole-body MRI and PET-CT plus a fully "
            "automated NABL clinical laboratory for all specialties."
        ),
        image_url="https://images.unsplash.com/photo-1587351021759-3e566b6af7cc?auto=format&fit=crop&w=1200&q=80",
        rating="4.5",
        review_count=2980,
        phone="011-2658 8500",
        panels="CGHS, ECHS, Corporate Empanelment",
        tests=[
            ("Cardiac MRI", "MRI Scan", "MRI assessment of heart structure, myocardium and viability.", Decimal("12500.00")),
            ("Coronary CT Angiography", "Cardiology", "Non-invasive 3D imaging of coronary arteries.", Decimal("9500.00")),
            ("Lipid Profile (Cardiac Risk)", "Cardiology", "Cholesterol and triglyceride screening for heart risk.", Decimal("600.00")),
            ("Complete Blood Count (CBC)", "Blood Test", "Routine screening for anaemia and infection.", Decimal("300.00")),
            ("Whole Body PET-CT", "CT Scan", "Molecular imaging for oncology and metabolic scans.", Decimal("20000.00")),
            ("EEG Brain Mapping", "Neurology", "Electroencephalogram monitoring of brain electrical activity.", Decimal("2100.00")),
            ("Nerve Conduction Study (NCS)", "Neurology", "Measures speed of electrical signals in nerves.", Decimal("2600.00")),
            ("Comprehensive Health Screening", "Full Body Checkup", "80+ parameters spanning cardiac, metabolic and imaging.", Decimal("6799.00")),
        ],
    ),
]


def seed_centres(db: Session) -> None:
    for centre_data in CENTRES:
        tests = centre_data["tests"]
        centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.name == centre_data["name"]).first()
        if not centre:
            centre = DiagnosticCentre(name=centre_data["name"])
            db.add(centre)

        for field in CENTRE_FIELDS:
            value = centre_data.get(field)
            if field == "starting_price" and value is None:
                value = min(price for _, _, _, price in tests)
            setattr(centre, field, value)
        db.flush()

        for name, category, description, price in tests:
            existing_test = (
                db.query(DiagnosticTest)
                .filter(DiagnosticTest.centre_id == centre.id, DiagnosticTest.name == name)
                .first()
            )
            if not existing_test:
                db.add(
                    DiagnosticTest(
                        centre_id=centre.id,
                        name=name,
                        category=category,
                        description=description,
                        price=price,
                    )
                )
            else:
                existing_test.category = category
                existing_test.description = description
                existing_test.price = price

    _drop_stale_centres(db)
    db.commit()


def _drop_stale_centres(db: Session) -> None:
    """Remove previously seeded centres that are no longer part of the catalogue.

    Centres with existing bookings are kept so historical invoices stay valid.
    """
    known_names = {entry["name"] for entry in CENTRES}
    stale = (
        db.query(DiagnosticCentre)
        .filter(DiagnosticCentre.name.notin_(known_names))
        .all()
    )
    for centre in stale:
        if centre.bookings:
            continue
        db.delete(centre)
