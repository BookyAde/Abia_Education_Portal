
# 🏛️ Abia State Real-Time Education Portal

### Live · Transparent · Government-Ready · Built with Streamlit, PostgreSQL & Python

This project is a **full-stack real-time data management and analytics platform** built for Abia State’s Education Sector.
It enables **schools** to submit data, **admins** to approve or reject submissions, and **government stakeholders** to monitor live metrics across **all 17 LGAs in Abia State**.

---

## 🚀 Key Features

### ✅ **1. Live Dashboard**

* Real-time charts powered directly from the **Data Warehouse (DWH)**
* Displays:

  * Total Enrollment by LGA
  * Pupil-Teacher Ratio
  * Total Teachers
  * LGA Rankings
* Auto-refresh with one click
* Clean layout with responsive design

---

### 📝 **2. Submit Data (Schools Panel)**

Schools can submit:

* School Name
* LGA
* Total Students
* Total Teachers
* Contact Information

✔ Validation included
✔ Automatically saved to the database
✔ Marked as *pending* until approved by admin
✔ School receives automatic email updates

---

### 📥 **3. Request Dataset**

Anyone (researchers, NGOs, government bodies) can request a full dataset.
The system automatically:

* Generates a fresh **Excel file** from approved records
* Sends it via email with the requestor’s details included

---

### 🔐 **4. Admin Panel**

Admins can:

* View all pending submissions
* Approve or Reject data
* Automatically notify schools via email
* See detailed metrics for each entry

✔ Built-in email notifications
✔ Full audit trail via timestamps
✔ Secure access

---

### 🧰 **5. Tech Stack**

| Layer              | Technology               |
| ------------------ | ------------------------ |
| **Frontend**       | Streamlit + Custom CSS   |
| **Backend**        | Python + SQLAlchemy      |
| **Database**       | PostgreSQL (DWH + OLTP)  |
| **Email Delivery** | Gmail SMTP via `smtplib` |
| **Data Export**    | Pandas + XlsxWriter      |

---

## 🗂️ Project Structure

```
/abia_education_portal
│── app.py
│── styles/
│   └── styles.css
│── assets/
│── requirements.txt
│── README.md
```

---

## 🛠️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/abia-education-portal.git
cd abia-education-portal
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Streamlit Secrets

Run:

```
streamlit secrets
```

Add the following:

```toml
DB_USER="your_user"
DB_PASSWORD="your_password"
DB_HOST="your_host"
DB_PORT="5432"
DB_NAME="your_dbname"

EMAIL_USER="your_email@gmail.com"
EMAIL_PASSWORD="your_app_password"
```

### 5️⃣ Run the App

```bash
streamlit run app.py
```

---

## 📊 Database Tables

### `dwh.fact_abia_metrics`

Used for dashboard calculations
Stores aggregated education metrics per LGA.

### `school_submissions`

Stores raw school submissions for approval.

| Column           | Description         |
| ---------------- | ------------------- |
| school_name      | Submitted school    |
| lga_name         | LGA of school       |
| enrollment_total | # of pupils         |
| teachers_total   | # of teachers       |
| submitted_by     | Submitter name      |
| email            | Submitter email     |
| submitted_at     | Timestamp           |
| approved         | TRUE / FALSE / NULL |

---

## 📧 Email Notifications

The portal automatically handles:

* Approval emails
* Rejection emails
* Dataset request emails with attached Excel file

Uses:

```python
smtplib.SMTP_SSL('smtp.gmail.com', 465)
```

---

## 🧪 Testing Checklist

Before deployment, ensure:

* [ ] Database connection successful
* [ ] Submissions save correctly
* [ ] Admin approve/reject works
* [ ] Emails deliver successfully
* [ ] Excel export downloads well
* [ ] Dashboard loads with no SQL errors
* [ ] CSS renders correctly

---

## 👨‍💻 Creator

**Alabi Winner (BookyAde)**
Data Engineer • Python Developer

📧 Email: **[alabiwinner9@gmail.com](mailto:alabiwinner9@gmail.com)**
🌐 GitHub: **[https://github.com/BookyAde](https://github.com/BookyAde)**

---

## ⭐ Support the Project

If this project inspires you or helps you, consider giving it a **star** ⭐ on GitHub.
